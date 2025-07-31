# _plugins/hashtags.rb
# frozen_string_literal: true

require "jekyll"
require "nokogiri"
require "cgi"

module Jekyll
  module Hashtags
    BODY_OPEN_RE   = %r!<body[^>]*>!i.freeze
    BODY_CLOSE_TAG = "</body>"
    DEFAULTS = {
      "base_url"    => "",             # e.g. "https://twitter.com"
      "tag_url"     => "/tags/%{tag}", # interpolated with the tag text
      "tag_pattern" => '#([\p{L}\w-]+)' # Unicode letters + word chars + dash
    }.freeze

    # ------------------------------------------------------------------
    # Hook entry-point
    # ------------------------------------------------------------------
    def self.hashtag_it(doc)
      return unless taggable?(doc)

      cfg            = config_for(doc)
      filter         = Filter.new(cfg)
      content        = doc.output

      if content =~ BODY_OPEN_RE
        head, body_tag, rest = content.partition(BODY_OPEN_RE)
        body, close_tag, tail = rest.partition(BODY_CLOSE_TAG)
        processed = filter.call(body)

        doc.output = +"#{head}#{body_tag}#{processed}#{close_tag}#{tail}"
      else
        doc.output = filter.call(content)
      end
    end

    # A document is taggable when it’s HTML and will actually be written.
    def self.taggable?(doc)
      (doc.is_a?(Jekyll::Page) || doc.write?) &&
        (doc.output_ext == ".html" || doc.permalink&.end_with?("/"))
    end

    # Site-wide settings merged with front-matter overrides
    def self.config_for(doc)
      site_cfg  = doc.site.config.fetch("jekyll-hashtags", {})
      page_cfg  = doc.data.fetch("jekyll-hashtags", {})
      defaults  = DEFAULTS.dup

      defaults.merge!(site_cfg.is_a?(Hash) ? site_cfg : { "base_url" => site_cfg })
      defaults.merge!(page_cfg.is_a?(Hash) ? page_cfg : { "base_url" => page_cfg })
    end

    # ------------------------------------------------------------------
    # Nokogiri-based filter
    # ------------------------------------------------------------------
    class Filter
      def initialize(cfg)
        @base_url      = cfg["base_url"].to_s.chomp("/")
        @tag_url_tmpl  = cfg["tag_url"].to_s
        pattern       = cfg["tag_pattern"].to_s
        @regex = Regexp.new(pattern, 0, "u")
      end

      # Public: run the filter on an HTML string
      def call(html)
        frag = Nokogiri::HTML::DocumentFragment.parse(html)
        walk(frag)
        frag.to_html
      end

      private

      # Depth-first traversal of the DOM; only mutate text nodes that are
      # *not* inside ©, <script>, <style>, <code>, or existing links.
      def walk(node)
        node.children.each do |child|
          next if child.element? && %w[a code pre script style].include?(child.name)

          if child.text?
            child.replace(linkify(child.text))
          else
            walk(child)
          end
        end
      end

      # Converts “#tag” → <a ...>#tag</a>
      def linkify(text)
        text.gsub(@regex) do |_|
          tag = Regexp.last_match(1)
          href = File.join(@base_url, format(@tag_url_tmpl, tag: CGI.escape(tag)))
          %(<a href="#{href}" class="hashtag">##{CGI.escapeHTML(tag)}</a>)
        end
      end
    end
  end
end

# ------------------------------------------------------------
# Jekyll integration
# ------------------------------------------------------------
Jekyll::Hooks.register(%i[pages documents], :post_render) do |doc|
  Jekyll::Hashtags.hashtag_it(doc)
end

# Optional Liquid filter so you can run {{ content | hashtagify }}
module Jekyll
  module HashtagFilter
    def hashtagify(input)
      site_cfg = @context.registers[:site].config
      cfg      = Jekyll::Hashtags.config_for(OpenStruct.new(site: OpenStruct.new(config: site_cfg), data: {}))
      Jekyll::Hashtags::Filter.new(cfg).call(input.to_s)
    end
  end
end
Liquid::Template.register_filter(Jekyll::HashtagFilter)
