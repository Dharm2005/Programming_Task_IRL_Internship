import streamlit as st
from utils.transcript import get_transcript
from utils.pdf_generator import save_to_pdf
from utils.local_summarizer import summarize_text
import os

def extract_video_id(url):
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return url

# Page config
st.set_page_config(page_title="YouTube Summarizer", layout="centered")

st.title("🎥 YouTube Video Summarizer")
st.write("Convert YouTube videos into summaries, articles, and PDF")

# Input
url = st.text_input("Enter YouTube URL")

if st.button("Generate"):
    if url:
        with st.spinner("Processing... ⏳"):

            # Show video (nice UI touch)
            st.video(url)

            video_id = extract_video_id(url)

            # Step 1: Transcript
            transcript = get_transcript(video_id)

            # Step 2: Summary (LOCAL MODEL)
            summary = summarize_text(transcript)

            # Step 3: Article (MANUAL GENERATION)
            article = f"""# YouTube Video Summary

## Key Points
{summary}

## Detailed Explanation
{transcript[:1000]}
"""

            # Ensure output folder exists
            os.makedirs("output", exist_ok=True)

            # Save PDF
            pdf_path = "output/result.pdf"
            save_to_pdf(article, pdf_path)

        st.success("✅ Done!")

        # Show results
        st.subheader("📌 Summary")
        st.write(summary)

        st.subheader("📰 Article")
        st.markdown(article)

        # Download PDF
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download PDF",
                data=f,
                file_name="summary.pdf",
                mime="application/pdf"
            )

    else:
        st.warning("⚠️ Please enter a YouTube URL")