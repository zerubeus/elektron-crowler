import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from bs4 import BeautifulSoup

THREAD_ID = "222373"
BASE_URL = f"https://www.elektronauts.com/t/{THREAD_ID}.json"


def get_post_ids():
    """Fetch post IDs directly from the URL."""
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        data = response.json()
        return data.get("post_stream", {}).get("stream", [])
    else:
        print(f"Failed to fetch initial data: {response.status_code}")
        return []


def fetch_posts_in_batches(post_ids, batch_size=20):
    """Fetch posts in batches and return their 'cooked' content."""
    cooked_contents = []
    posts_url = f"https://www.elektronauts.com/t/{THREAD_ID}/posts.json"

    for i in range(0, len(post_ids), batch_size):
        batch = post_ids[i : i + batch_size]
        response = requests.get(posts_url, params={"post_ids[]": batch})
        if response.status_code == 200:
            posts = response.json().get("post_stream", {}).get("posts", [])
            for post in posts:
                cooked_contents.append(
                    {"id": post.get("id"), "content": post.get("cooked", "")}
                )
        else:
            print(f"Failed to fetch batch {i//batch_size + 1}: {response.status_code}")
    return cooked_contents


def html_to_text(html_content):
    """Convert HTML content to plain text while preserving basic formatting."""
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove audio elements as they can't be represented in PDF
    for audio in soup.find_all("audio"):
        audio.decompose()
    # Convert emoji images to their alt text
    for img in soup.find_all("img"):
        if "emoji" in img.get("class", []):
            img.replace_with(img.get("alt", ""))
    return soup.get_text()


def create_pdf(cooked_contents, output_file):
    """Create a PDF document from the thread contents."""
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()

    # Create custom style for posts
    post_style = ParagraphStyle(
        "PostStyle",
        parent=styles["Normal"],
        spaceBefore=20,
        spaceAfter=20,
        leading=14,
    )

    # Create the PDF content
    elements = []
    for post in cooked_contents:
        # Convert HTML content to plain text
        text_content = html_to_text(post["content"])
        # Add post ID as a header
        elements.append(Paragraph(f"Post #{post['id']}", styles["Heading2"]))
        # Add the post content
        elements.append(Paragraph(text_content, post_style))
        elements.append(Spacer(1, 20))

    # Build the PDF
    doc.build(elements)


# Main execution
post_ids = get_post_ids()
all_cooked_contents = fetch_posts_in_batches(post_ids)

output_file = f"thread_content_{THREAD_ID}.pdf"
create_pdf(all_cooked_contents, output_file)

print(f"Thread content saved to {output_file}")
