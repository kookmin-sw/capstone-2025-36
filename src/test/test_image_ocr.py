import unittest
from unittest.mock import MagicMock, patch
import io
import base64
from PIL import Image
from dotenv import load_dotenv
from paddleocr import PaddleOCR
from transformers import pipeline, AutoProcessor, AutoModelForImageTextToText
from ..parsers.image_ocr import ImageOCR  # Assuming your code is in image_ocr.py

load_dotenv()

class TestImageOCR(unittest.TestCase):

    def setUp(self):
        self.image_ocr = ImageOCR()
        self.mock_image = Image.new('RGB', (100, 100), color='red')
        self.mock_binary_image = io.BytesIO()
        self.mock_image.save(self.mock_binary_image, format='PNG')
        self.mock_encoded_image = base64.b64encode(self.mock_binary_image.getvalue()).decode('utf-8')

    def test_init(self):
        self.assertIsInstance(self.image_ocr.ocr_model, PaddleOCR)
        self.assertIsNotNone(self.image_ocr.image_classifier)
        self.assertIsInstance(self.image_ocr.formula_processor, AutoProcessor)
        self.assertIsInstance(self.image_ocr.formula_model, AutoModelForImageTextToText)
        self.assertEqual(self.image_ocr.formula_prompt, self.image_ocr.formula_processor.apply_chat_template(FORMULA_OCR_MESSAGE, add_generation_prompt=True))

    @patch.object(ImageOCR, '_classificate_image')
    @patch.object(ImageOCR, '_extract_text_from_img')
    def test_convert_img_to_txt_text_category(self, mock_extract_text, mock_classify):
        mock_classify.return_value = 'Text'
        expected_text = "extracted text"
        mock_extract_text.return_value = expected_text
        result = self.image_ocr.convert_img_to_txt(self.mock_encoded_image)
        self.assertEqual(result, expected_text)
        mock_classify.assert_called_once()
        mock_extract_text.assert_called_once()

    @patch.object(ImageOCR, '_classificate_image')
    @patch.object(ImageOCR, '_extract_formula_from_img')
    def test_convert_img_to_txt_formula_category(self, mock_extract_formula, mock_classify):
        mock_classify.return_value = 'Formula'
        expected_latex = r"$\frac{a}{b}$"
        mock_extract_formula.return_value = expected_latex
        result = self.image_ocr.convert_img_to_txt(self.mock_encoded_image)
        self.assertEqual(result, fr"{expected_latex}")
        mock_classify.assert_called_once()
        mock_extract_formula.assert_called_once()

    @patch.object(ImageOCR, '_classificate_image')
    def test_convert_img_to_txt_other_category(self, mock_classify):
        mock_classify.return_value = 'Graph'
        result = self.image_ocr.convert_img_to_txt(self.mock_encoded_image)
        self.assertEqual(result, 'Graph')
        mock_classify.assert_called_once()

    def test_convert_img_to_txt_invalid_image(self):
        invalid_encoded_image = "invalid_base64"
        result = self.image_ocr.convert_img_to_txt(invalid_encoded_image)
        self.assertIsNone(result)

    @patch.object(pipeline, '__call__')
    def test_classificate_image_success(self, mock_pipeline):
        mock_pipeline.return_value = [{'label': 'Text', 'score': 0.9}]
        result = self.image_ocr._classificate_image(self.mock_image)
        self.assertEqual(result, 'Text')
        mock_pipeline.assert_called_once()

    @patch.object(pipeline, '__call__')
    def test_classificate_image_failure(self, mock_pipeline):
        mock_pipeline.side_effect = Exception("Classification error")
        result = self.image_ocr._classificate_image(self.mock_image)
        self.assertIsNone(result)

    @patch.object(AutoProcessor, 'from_pretrained')
    @patch.object(AutoModelForImageTextToText, 'from_pretrained')
    @patch.object(AutoProcessor, 'apply_chat_template')
    @patch.object(AutoModelForImageTextToText, 'generate')
    @patch.object(AutoProcessor, 'batch_decode')
    @patch.object(ImageOCR, '_convert_text_to_latex')
    def test_extract_formula_from_img_success(self, mock_convert_latex, mock_batch_decode, mock_generate, mock_apply_template, mock_model_pretrained, mock_processor_pretrained):
        mock_processor = MagicMock()
        mock_model = MagicMock()
        mock_processor_pretrained.return_value = mock_processor
        mock_model_pretrained.return_value = mock_model
        mock_apply_template.return_value = "prompt"
        mock_processor.return_value = {"pixel_values": "mock_values", "input_ids": "mock_ids"}
        mock_generate.return_value = ["generated_id"]
        mock_batch_decode.return_value = ["extracted formula"]
        mock_convert_latex.return_value = r"$\sqrt{x}$"

        result = self.image_ocr._extract_formula_from_img(self.mock_image)
        self.assertEqual(result, r"$\sqrt{x}$")
        mock_processor_pretrained.assert_called_once_with("ds4sd/SmolDocling-256M-preview", use_fast=True)
        mock_model_pretrained.assert_called_once_with("ds4sd/SmolDocling-256M-preview")
        mock_apply_template.assert_called_once_with(FORMULA_OCR_MESSAGE, add_generation_prompt=True)
        mock_processor.assert_called_once_with(text="prompt", images=[self.mock_image], return_tensors="pt")
        mock_generate.assert_called_once()
        mock_batch_decode.assert_called_once_with(["generated_id"], skip_special_tokens=True)
        mock_convert_latex.assert_called_once_with("extracted formula")

    def test_convert_text_to_latex_with_formula(self):
        text_with_formula = "User: Extract mathematical expressions in LaTeX format Assistant: 0>0>500>500> a/b + c"
        expected_latex = r"$a/b + c$"
        result = self.image_ocr._convert_text_to_latex(text_with_formula)
        self.assertEqual(result, expected_latex)

    def test_convert_text_to_latex_without_formula(self):
        text_without_formula = "This is a text without any formula."
        result = self.image_ocr._convert_text_to_latex(text_without_formula)
        self.assertEqual(result, text_without_formula)

    @patch.object(PaddleOCR, 'ocr')
    def test_extract_text_from_image_with_paddle_success(self, mock_ocr):
        mock_ocr.return_value = [[(0, 0, 10, 10), ('sample', 0.9)]]
        result = self.image_ocr._extract_text_from_image_with_paddle(self.mock_binary_image.getvalue())
        self.assertEqual(result, "sample")
        mock_ocr.assert_called_once()

    @patch.object(PaddleOCR, 'ocr')
    def test_extract_text_from_image_with_paddle_multiple_lines(self, mock_ocr):
        mock_ocr.return_value = [[(0, 0, 10, 10), ('line1', 0.9)], [(0, 15, 25, 25), ('line2', 0.8)]]
        result = self.image_ocr._extract_text_from_image_with_paddle(self.mock_binary_image.getvalue())
        self.assertEqual(result, "line1\nline2")
        mock_ocr.assert_called_once()

    @patch.object(PaddleOCR, 'ocr')
    def test_extract_text_from_image_with_paddle_empty_result(self, mock_ocr):
        mock_ocr.return_value = [[]]
        result = self.image_ocr._extract_text_from_image_with_paddle(self.mock_binary_image.getvalue())
        self.assertEqual(result, "")
        mock_ocr.assert_called_once()

if __name__ == '__main__':
    unittest.main()