from dataclasses import dataclass
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from bs4 import BeautifulSoup

# Constants
THREAD_ID: str = "222373"
BASE_URL: str = f"https://www.elektronauts.com/t/{THREAD_ID}.json"
POSTS_URL: str = f"https://www.elektronauts.com/t/{THREAD_ID}/posts.json"
DEFAULT_BATCH_SIZE: int = 20


@dataclass
class ForumPost:
    """Represents a forum post with its ID and content."""

    post_id: int
    content: str


class ElektronautsClient:
    """Client for interacting with the Elektronauts forum API."""

    @staticmethod
    def get_post_ids() -> list[int]:
        """
        Fetch post IDs from the forum thread.

        Returns:
            list[int]: List of post IDs in the thread.
        """
        response = requests.get(BASE_URL)
        response.raise_for_status()
        data = response.json()
        return data.get("post_stream", {}).get("stream", [])

    @staticmethod
    def fetch_posts_in_batches(
        post_ids: list[int], batch_size: int = DEFAULT_BATCH_SIZE
    ) -> list[ForumPost]:
        """
        Fetch posts in batches to avoid overloading the server.

        Args:
            post_ids: List of post IDs to fetch
            batch_size: Number of posts to fetch in each batch

        Returns:
            list[ForumPost]: List of forum posts with their content
        """
        posts = []
        for i in range(0, len(post_ids), batch_size):
            batch = post_ids[i : i + batch_size]
            response = requests.get(POSTS_URL, params={"post_ids[]": batch})
            response.raise_for_status()

            batch_posts = response.json().get("post_stream", {}).get("posts", [])
            posts.extend(
                ForumPost(post_id=post["id"], content=post.get("cooked", ""))
                for post in batch_posts
            )
        return posts


class HTMLProcessor:
    """Handles HTML content processing and conversion."""

    @staticmethod
    def html_to_text(html_content: str) -> str:
        """
        Convert HTML content to plain text while preserving basic formatting.

        Args:
            html_content: Raw HTML content to process

        Returns:
            str: Processed plain text content
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove audio elements as they can't be represented in PDF
        for audio in soup.find_all("audio"):
            audio.decompose()

        # Convert emoji images to their alt text
        for img in soup.find_all("img"):
            if "emoji" in img.get("class", []):
                img.replace_with(img.get("alt", ""))

        return soup.get_text()


class PDFGenerator:
    """Handles PDF document generation from forum posts."""

    def __init__(self, output_file: str):
        """
        Initialize PDF generator.

        Args:
            output_file: Path to the output PDF file
        """
        self.doc = SimpleDocTemplate(output_file, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.post_style = ParagraphStyle(
            "PostStyle",
            parent=self.styles["Normal"],
            spaceBefore=20,
            spaceAfter=20,
            leading=14,
        )

    def create_pdf(self, posts: list[ForumPost]) -> None:
        """
        Create a PDF document from forum posts.

        Args:
            posts: List of forum posts to include in the PDF
        """
        elements = []
        for post in posts:
            text_content = HTMLProcessor.html_to_text(post.content)
            elements.append(Paragraph(f"Post #{post.post_id}", self.styles["Heading2"]))
            elements.append(Paragraph(text_content, self.post_style))
            elements.append(Spacer(1, 20))

        self.doc.build(elements)


def main() -> None:
    """Main execution function."""
    client = ElektronautsClient()
    post_ids = client.get_post_ids()
    posts = client.fetch_posts_in_batches(post_ids)

    output_file = f"thread_content_{THREAD_ID}.pdf"
    pdf_generator = PDFGenerator(output_file)
    pdf_generator.create_pdf(posts)

    print(f"Thread content saved to {output_file}")


if __name__ == "__main__":
    main()
