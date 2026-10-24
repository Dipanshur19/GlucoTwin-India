import pathlib,re,sys,json
root=pathlib.Path(__file__).resolve().parents[1]
required=['README.md','LICENSE','DATA_SOURCES.md','MODEL_CARD.md','requirements.txt','app.py','models/glucotwin.joblib','data/source_csv.zip','docs/GlucoTwin_Presentation.pdf','docs/GlucoTwin_Presentation.pptx','docs/GlucoTwin_Architecture.pdf','docs/GlucoTwin_Technical_Report.pdf','docs/Demo_Script.md','results/summary.json']
missing=[n for n in required if not (root/n).is_file() or (root/n).stat().st_size==0]
text=(root/'README.md').read_text();block=text.split('<!-- VIDEO_LINK_START -->')[1].split('<!-- VIDEO_LINK_END -->')[0]
video=bool(re.search(r'https://(?:www\.)?(?:youtube\.com|youtu\.be)/',block))
print('Required files:', 'PASS' if not missing else 'MISSING '+str(missing))
print('Actual video link:', 'PRESENT - verify public playback manually' if video else 'PENDING - upload the supplied MP4 and run finalize_submission.py')
print('Repository/public-link access: requires a signed-out browser check.')
sys.exit(0 if not missing and video else 1)
