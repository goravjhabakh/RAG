import os 
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

def convert_to_markdown(input_folder, output_folder):
    converter = PdfConverter(artifact_dict=create_model_dict())
    converted = 0

    for doc in os.listdir(input_folder):
        if doc.replace('.pdf','.md') in os.listdir(output_folder): continue
        rendered = converter(os.path.join(input_folder,doc))
        text, metadata, images = text_from_rendered(rendered)

        output_path = os.path.join(output_folder,doc.replace('.pdf','.md'))
        with open(output_path,'w',encoding='utf-8') as md:
            md.write(text)
        converted += 1

    print(f'Converted {converted} to markdown')