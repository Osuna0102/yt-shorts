from PIL import Image, ImageDraw, ImageFont

def create_text_image(text, image_file, width=1080, height=1920, font_size=48):
    # Create an image with Pillow
    background_color = (0, 0, 0, 0)  # Transparent background
    text_color = "white"
    outline_color = "black"  # Outline color for better contrast

    image = Image.new("RGBA", (width, height), color=background_color)  # Use RGBA for transparency
    draw = ImageDraw.Draw(image)

    # Use Impact font or fallback to Arial
    try:
        font = ImageFont.truetype("impact.ttf", font_size)  # Impact font for bold text
    except IOError:
        font = ImageFont.truetype("arial.ttf", font_size)  # Fallback to Arial if Impact is not available

    # Wrap text to fit within the width
    max_width = width - 40  # Leave some padding on the sides
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if draw.textlength(test_line, font=font) <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    # Draw text with outline
    y_text = 100  # Start a bit lower for better visual balance
    for line in lines:
        text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:4]
        
        # Draw outline
        outline_range = 2  # Outline thickness
        for x_offset in range(-outline_range, outline_range + 1):
            for y_offset in range(-outline_range, outline_range + 1):
                draw.text(((width - text_width) / 2 + x_offset, y_text + y_offset), line, font=font, fill=outline_color)
        
        # Draw main white text
        draw.text(((width - text_width) / 2, y_text), line, font=font, fill=text_color)
        y_text += text_height + 10  # Add some space between lines

    # Save the image
    image.save(image_file, resample=Image.LANCZOS)

# Example usage
if __name__ == "__main__":
    create_text_image("This is a test text for Reddit stories, Reels, and TikToks!", "output_image.png")