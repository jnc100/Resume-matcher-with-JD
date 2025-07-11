from flask import Flask,request,render_template
import os
import fitz
import textract
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity  
from hf_llm import llm_match_resume
import tempfile
import docx2txt
def extract_text(file):
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "".join([page.get_text() for page in doc])
    elif filename.endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file.read())
            return docx2txt.process(tmp.name)
    elif filename.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        return "Unsupported file format"

def home():
    return render_template("matchresume.html")


def llm_matcher():
    if 'resume' not in request.files or 'jd' not in request.files:
        return "Please upload both resume and job description.", 400

    resume_file = request.files['resume']
    jd_file = request.files['jd']

    resume_text = extract_text(resume_file)
    jd_text = extract_text(jd_file)

    result = llm_match_resume(resume_text, jd_text)

    return render_template("matchresume.html", feedback=result)






    

    

app=Flask(__name__)
app.config['UPLOAD_FOLDER']='uploads/' 
@app.route("/")
@app.route("/matcher",methods=['GET','POST'])
@app.route("/matcher", methods=['GET', 'POST'])
@app.route('/llm_matcher', methods=['POST'])
def matcher():
    resumes = []
    job_description = None

    if request.method == 'POST':
        job_description = request.form.get('job_description', '').strip()
        resume_files = request.files.getlist('resumes')

        # Check if any resumes were uploaded (i.e. filenames are non-empty)
        has_valid_resume = any(resume.filename for resume in resume_files)

        if not has_valid_resume or not job_description:
            return render_template('matchresume.html', message="Please upload resume and post job")

        # Save resumes if provided
        for resume in resume_files:
            if resume.filename:
                filename = os.path.join(app.config['UPLOAD_FOLDER'], resume.filename)
                resume.save(filename)
                resumes.append(filename)
        resume_texts = [extract_text(resume) for resume in resumes]
        vectorizer=TfidfVectorizer().fit_transform([job_description]+resume_texts)
        vectors=vectorizer.toarray()
        job_vector=vectors[0]
        resumes_vector=vectors[1:]
    
        similarities=cosine_similarity([job_vector],resumes_vector)
    
        top_indices=similarities[0].argsort()[-3:][::-1]
        top_resumes=[resume_files[i] for i in top_indices]
        similarity_score=[similarities[0][i] for i in top_indices]


        return render_template('matchresume.html', message="Top Matching Resumes:",top_resumes=top_resumes, )

    return render_template('matchresume.html')
   




def matchresume():
    return render_template('matchresume.html')

if __name__=="__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

    