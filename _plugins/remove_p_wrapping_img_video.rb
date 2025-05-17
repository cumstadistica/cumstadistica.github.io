Jekyll::Hooks.register [:pages, :documents], :post_render do |doc|
  next unless doc.output_ext == '.html'

  # Desenrollar <img> solitos
  doc.output.gsub!(/<p>\s*(<img[^>]+>)\s*<\/p>/, '\1')

  # Desenrollar <a><img></img></a>
  doc.output.gsub!(/<p>\s*(<a[^>]+>\s*<img[^>]+>\s*<\/a>)\s*<\/p>/, '\1')

  # Desenrollar <video> solitos
  doc.output.gsub!(/<p>\s*(<video[^>]*>.*?<\/video>)\s*<\/p>/m, '\1')

  # Desenrollar <a><video></video></a>
  doc.output.gsub!(/<p>\s*(<a[^>]*>\s*<video[^>]*>.*?<\/video>\s*<\/a>)\s*<\/p>/m, '\1')
end
