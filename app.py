from pydoc import render_doc
from pytube import YouTube
import youtube_dl
import time
from flask import Flask, send_file, redirect, render_template, request, session, url_for, after_this_request
import os

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "Doggy"

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        url = request.form.get("url")
        session["url"] = url
    
        video = YouTube(
                    url,
                    use_oauth=False
        )

        Title = video.title
        Thumbnail = video.thumbnail_url
        Duration = time.strftime('%H:%M:%S', time.gmtime(video.length))
        session["Title"] = Title
        session["Thumbnail"] = Thumbnail
        session["Duration"] = Duration

        

        streams = set()
        for stream in video.streams.filter(type="video"):
            streams.add(stream.resolution)
        streams = sorted(streams, key=lambda Res: int(Res[:-1]), reverse=True)
        session["streams"] = streams

        return redirect(url_for('.videoinfo', Title=Title, Thumbnail=Thumbnail, Duration=Duration, streams=streams, **request.args))

    else:
        return render_template("index.html")

@app.route("/videoinfo", methods=["GET", "POST"])
def videoinfo():

    Title = session.get("Title", None)

    if request.method == "POST":

        Res = request.form.get("Res")
        Res = Res.replace("p", "")

        url = session.get("url", None)

        ydl_opts = {
            'format': f'bestvideo[height={Res}, ext=mp4]+bestaudio/best[height={Res}, ext=mp4]/best[height={Res}]',
            'merge_output_format': 'mp4',
            'continuedl': False,
            'outtmpl': 'y2Bro - %(title)s.%(ext)s',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # @after_this_request 
        # def remove_video():
        #     time.sleep(10)
        #     os.remove(f"y2Bro - {Title}.mp4")
        #     return redirect("/")

        return send_file(path_or_file=f"y2Bro - {Title}.mp4", as_attachment=True)

    else:
        Thumbnail = session.get("Thumbnail", None)
        Duration = session.get("Duration", None)
        streams = session.get("streams", None)
        return render_template("videoinfo.html", Title=Title, Thumbnail=Thumbnail, Duration=Duration, streams=streams)

# @app.route("/send_video")
# def send_video():
#     Title = session.get("Title", None)
#     return send_file(path_or_file=f"y2Bro - {Title}.mp4", as_attachment=True)








# @app.after_request
# def delete_video(response):

#     if request.endpoint=="videoinfo" and request.method == "POST":
#         time.sleep(10)
#         Title = session.get("Title", None)
#         os.remove(f"y2Bro - {Title}.mp4")

#     return response
