from unstructured.partition.auto import partition
from logs.main import LOGGER
import warnings
warnings.filterwarnings("ignore", message="CropBox missing from /Page, defaulting to MediaBox")

logger = LOGGER.get_logger()

def partition_document(file_path: str) -> str:
    try:
        logger.info(f"Partitioning document: {file_path}")

        elements = partition(
            filename=file_path,
            infer_table_structure=True,
            include_page_breaks=True,
            extract_images=False
        )

        full_text_parts = []

        for element in elements:
            text = str(element)
            if text:
                full_text_parts.append(text)

        return "\n\n".join(full_text_parts)

    except Exception as e:
        logger.error(f"Error partitioning document {file_path}: {str(e)}")
        raise