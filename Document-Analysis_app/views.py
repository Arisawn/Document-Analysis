# # # chatgpt_app/views.py

# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import ResearchPaper
# from .serializers import ResearchPaperSerializer
# from django.http import JsonResponse
# from transformers import pipeline
# from transformers import AutoTokenizer, AutoModel
# from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
# from transformers import BertTokenizer, BertForQuestionAnswering
# from transformers import GPT2LMHeadModel, GPT2Tokenizer
# import torch

# tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
# model = GPT2LMHeadModel.from_pretrained("gpt2")

# class ChatGPTView(APIView):
#     def get(self, request, format=None):
#         papers = ResearchPaper.objects.all()
#         return render(request, 'upload_paper.html', {'papers': papers})

#     def post(self, request, format=None):
#         serializer = ResearchPaperSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             document = serializer.instance.document
#             document_text = self.extract_text_from_document(document)
#             question = request.data.get('question', '')
#             answer = self.get_answer(question, document_text)
#             print(f"Answer: {answer}")

#             # Return the answer as a JSON response
#             return JsonResponse({'answer': answer})

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def extract_text_from_document(self, document):
#         # Check if the document is a file object or a file path
#         if hasattr(document, 'read'):
#             # It's a file object; read the content
#             try:
#                 return document.read().decode('utf-8', errors='ignore')
#             except UnicodeDecodeError:
#                 try:
#                     return document.read().decode('iso-8859-1')
#                 except Exception as e:
#                     return str(e)
#         else:
#             # It's a file path; read the content from the file
#             try:
#                 with open(document, 'r', encoding='utf-8', errors='ignore') as file:
#                     return file.read()
#             except UnicodeDecodeError:
#                 try:
#                     with open(document, 'r', encoding='iso-8859-1') as file:
#                         return file.read()
#                 except Exception as e:
#                     return str(e)

#     def get_answer(self, question, document_text):
#         # Concatenate the question and document with a separator token
#         input_text = f"{question} [SEP] {document_text}"

#         # Generate a response using ChatGPT
#         response = self.generate_response(input_text)

#         print(f"Generated Response: {response}")
#         return response

#     def generate_response(self, input_text):
#         # Encode the input text
#         inputs = tokenizer.encode(input_text, return_tensors='pt')

#         # Generate a response using the model
#         outputs = model.generate(inputs, max_length=100, num_return_sequences=1, no_repeat_ngram_size=2)

#         # Decode the response
#         response = tokenizer.decode(outputs[0], skip_special_tokens=True)

#         return response


# chatgpt_app/views.py

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ResearchPaper
from .serializers import ResearchPaperSerializer
import fitz  
import tempfile
import os
from django.http import JsonResponse
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

class ChatGPTView(APIView):
    def get(self, request, format=None):
        papers = ResearchPaper.objects.all()
        return render(request, 'upload_paper.html', {'papers': papers})

    def post(self, request, format=None):
        serializer = ResearchPaperSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            document = serializer.instance.document
            document_text = self.extract_text_from_document(document)
            question = request.data.get('question', '')

            # Shorten the input text
            input_text = f"{question} [SEP] {document_text[:800]}"  # Adjust the length as needed
            answer = self.get_answer(input_text)
            print(f"Answer: {answer}")

            # Return the answer as a JSON response
            return JsonResponse({'answer': answer})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def extract_text_from_document(self, document):
        # Check if the document is a file object or a file path
        if hasattr(document, 'read'):
            # It's a file object; read the content
            try:
                return document.read().decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                try:
                    return document.read().decode('iso-8859-1')
                except Exception as e:
                    return str(e)
        else:
            # It's a file path; read the content from the file
            try:
                with open(document, 'r', encoding='utf-8', errors='ignore') as file:
                    return file.read()
            except UnicodeDecodeError:
                try:
                    with open(document, 'r', encoding='iso-8859-1') as file:
                        return file.read()
                except Exception as e:
                    return str(e)
    
    def extract_text_from_pdf(self, pdf_content):
    # Ensure pdf_content is in bytes format
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('utf-8')

    # Save the PDF content to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf.write(pdf_content)

        try:
        # Open the temporary file with PyMuPDF
            doc = fitz.open(temp_pdf.name)

        # Extract text from the PDF
            pdf_text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                pdf_text += page.get_text()

            return pdf_text

        finally:
        # Explicitly close the temporary file before trying to remove it
            temp_pdf.close()
            os.unlink(temp_pdf.name)              

    def get_answer(self, input_text):
        # Generate a response using ChatGPT
        response = self.generate_response(input_text)
        print(f"Generated Response: {response}")
        return response

    def generate_response(self, input_text):
    # Encode the input text
        inputs = tokenizer.encode(input_text, return_tensors='pt')

    # Generate a response using the model
        outputs = model.generate(inputs, max_length=500, num_return_sequences=1, no_repeat_ngram_size=2)

    # Decode the response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract text using PyMuPDF
        pdf_text = self.extract_text_from_pdf(response)

        return pdf_text