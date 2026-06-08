from groq import Groq
import base64
from dotenv import load_dotenv
import os 


class ImageAgent:
	def __init__(self):
		load_dotenv()
		self.client = Groq(api_key=os.environ["GROQ_API_KEY"])


	@staticmethod
	def read_file(file_path):
		with open(file_path, "r") as file:
			return file.read()


	@staticmethod
	def encode_image(image_path):
		with open(image_path, "rb") as image_file:
			return base64.b64encode(image_file.read()).decode('utf-8')


	def ask_vision_model(self, image_path):

		base64_image = ImageAgent.encode_image(image_path=image_path)

		chat_completion = self.client.chat.completions.create(
			messages=[
				{
					"role": "system",
					"content": ImageAgent.read_file(file_path="./context.txt")
				},
				{
					"role": "user",
					"content": [
						{"type": "text", "text": ImageAgent.read_file(file_path="./prompt.txt")},
						{
							"type": "image_url",
							"image_url": {
								"url": f"data:image/jpeg;base64,{base64_image}",
							},
						},
					], 
				}
			],

			model="meta-llama/llama-4-scout-17b-16e-instruct"
		)

		return chat_completion.choices[0].message.content



if __name__ == "__main__":
	image_agent_object = ImageAgent()

	image_path = "image.jpg"
	image_description = image_agent_object.ask_vision_model(image_path=image_path)
	
	print(image_description)