import argparse,json,pathlib,re
from urllib.parse import urlparse
root=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--video-url',required=True);p.add_argument('--repo-url',required=True);a=p.parse_args()
v=urlparse(a.video_url);r=urlparse(a.repo_url)
if v.scheme!='https' or v.netloc not in ('youtube.com','www.youtube.com','youtu.be') or not v.path.strip('/'):
 raise SystemExit('Use the actual HTTPS YouTube video URL.')
if r.scheme!='https' or r.netloc!='github.com' or len(r.path.strip('/').split('/'))!=2:
 raise SystemExit('Use an actual HTTPS GitHub repository URL.')
text=(root/'README.md').read_text()
replacement='<!-- VIDEO_LINK_START -->\n[Watch the 20-minute prototype demonstration]('+a.video_url+')\n<!-- VIDEO_LINK_END -->'
text=re.sub(r'<!-- VIDEO_LINK_START -->.*?<!-- VIDEO_LINK_END -->',lambda _:replacement,text,flags=re.S)
(root/'README.md').write_text(text)
(root/'submission_links.json').write_text(json.dumps({'video_url':a.video_url,'repository_url':a.repo_url,'visibility_verified_by_user':False},indent=2))
print('README updated. Verify both links without signing in before submission.')
