from pdf2image import convert_from_path
import pytesseract
import re
import pandas as pd 
import os

def extract_questions(pdf_path, psm=3, oem=3):
    # Convert PDF pages to images
    images = convert_from_path(pdf_path, dpi=300)
    questions = []
    
    # Regular expression to identify questions (assumes they start with numbers or letters)
    question_pattern = r'^\s*\d+\.|^\s*[a-zA-Z]\)'
    # question_pattern = r'^\s*(\d+\.\s*|[a-zA-Z]\)|[a-zA-Z]\))'


    for page_number, image in enumerate(images, start=1):
        # Extract text from the image
        config = f'--psm {psm} --oem {oem}'
        text = pytesseract.image_to_string(image, config=config)
        

        current_question = ""
        
        for line in text.split('\n'):
            if re.match(question_pattern, line):  # New question starts
                if current_question:  # Append the previous question to the list
                    questions.append(current_question.strip())
                current_question = line.strip()  # Start a new question
            else:  # Append additional lines to the current question
                current_question += f" {line.strip()}"

        # Add the last question if any
        if current_question:
            questions.append(current_question.strip())        
                
        

        print(f"Processed page {page_number}")
    
    return questions

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'  # Update the path if necessary

#creating folders if not exist
folders = ['datasets', 'pdfs', 'text']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

if not os.path.exists('text'):
    os.makedirs('text')
    
    
# Example usage
pdf_path = "pdfs/Engineering Mathematics III.pdf"  # Replace with your file path
name = (pdf_path.split('/')[1]).split('.')[0]
questions = extract_questions(pdf_path)

# store the output i.e. extracted questions
with open(f"text/{name}_questions.txt", "w") as file:
    for question in questions:
        file.write(f"{question}\n")

        
    
lists =[question.strip() for question in questions]

#just create dataframe but not save it to a csv file
# df = pd.DataFrame(lists, columns=['Questions'])

# Save the questions to a CSV file(not necessary for now since we have cleaned data at last)
pd.DataFrame(lists, columns=['Questions']).to_csv(f'datasets/{name}_questions.csv', index=False)
df = pd.read_csv(f'datasets/{name}_questions.csv')

#remove the elements before ')' and '.' in each row
unnecessary = []
for i in range(df.shape[0]):
    if ')' in df['Questions'][i][:4]:
        df['Questions'][i-1]+= ' ' +df['Questions'][i]
        unnecessary.append(i)
    elif '.' in df['Questions'][i][:4]:
        df['Questions'][i] = df['Questions'][i].split('.')[1]
    else:
        unnecessary.append(i)
df.drop(unnecessary, inplace=True)

df.to_csv(f'datasets/{name}_cleaned_questions.csv', index=False)