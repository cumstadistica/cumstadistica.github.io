Jekyll::Hooks.register [:pages, :documents], :post_render do |doc|
  next unless doc.output_ext == '.html'

  # Remove <p> tags that only contain an <img> (optionally with whitespace)
  doc.output.gsub!(/<p>\s*(<img[^>]+>)\s*<\/p>/, '\1')

  # Also catch <p> wrapping a link that wraps an image
  doc.output.gsub!(/<p>\s*(<a[^>]+>\s*<img[^>]+>\s*<\/a>)\s*<\/p>/, '\1')
end
