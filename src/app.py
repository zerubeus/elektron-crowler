from dataclasses import dataclass
import argparse
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from bs4 import BeautifulSoup

# Constants
DEFAULT_BATCH_SIZE: int = 20


def get_base_urls(thread_id: str) -> tuple[str, str]:
    """
    Generate base URLs for the thread.

    Args:
        thread_id: The forum thread ID

    Returns:
        tuple[str, str]: Base URL and posts URL for the thread
    """
    base_url = f"https://www.elektronauts.com/t/{thread_id}.json"
    posts_url = f"https://www.elektronauts.com/t/{thread_id}/posts.json"
    return base_url, posts_url


@dataclass
class ForumPost:
    """Represents a forum post with its ID and content."""

    post_id: int
    content: str


class ElektronautsClient:
    """Client for interacting with the Elektronauts forum API."""

    def __init__(self, thread_id: str):
        """
        Initialize the client with thread ID.

        Args:
            thread_id: The forum thread ID to fetch
        """
        self.base_url, self.posts_url = get_base_urls(thread_id)

    def get_post_ids(self) -> list[int]:
        """
        Fetch post IDs from the forum thread.

        Returns:
            list[int]: List of post IDs in the thread.
        """
        response = requests.get(self.base_url)
        response.raise_for_status()
        data = response.json()
        return data.get("post_stream", {}).get("stream", [])

    def fetch_posts_in_batches(
        self, post_ids: list[int], batch_size: int = DEFAULT_BATCH_SIZE
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
            response = requests.get(self.posts_url, params={"post_ids[]": batch})
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
    parser = argparse.ArgumentParser(
        description="Convert Elektronauts forum thread to PDF"
    )
    parser.add_argument(
        "thread_id",
        help="The thread ID from the Elektronauts forum URL (e.g., '222373')",
    )
    args = parser.parse_args()

    client = ElektronautsClient(args.thread_id)
    post_ids = client.get_post_ids()
    posts = client.fetch_posts_in_batches(post_ids)

    output_file = f"thread_content_{args.thread_id}.pdf"
    pdf_generator = PDFGenerator(output_file)
    pdf_generator.create_pdf(posts)

    print(f"Thread content saved to {output_file}")


if __name__ == "__main__":
    main()
