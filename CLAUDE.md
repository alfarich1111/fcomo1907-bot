# Project notes

Before writing any caption for CHELSEA UZ (@CHELSI_CHELSEAUZ_CFCUZ), read `data/emoji_guide_chelsea.md` and follow it.
It overrides any shorter emoji list in a task. Many stickers show a real face or logo, so never put one next to a different person, club or outlet.

# Post photos (both channels: CHELSEA UZ and @FComo1907)

The owner wants new, high-quality photos on every post. Follow this whenever you choose a photo:

- New: from the story itself, or from this season. The current kit, the current squad. No old photos when a recent one exists. Don't reuse a photo from the channel's recent posts.
- Quality: sharp, not stretched or heavily compressed. Get the largest version: on chelseafc.com images (res.cloudinary.com/chelsea-production) use c_fit,h_2000,w_3000,f_jpg, and elsewhere remove resize parameters such as ?w=, ?width=, ?resize= from the image URL.
- Run `python photo_check.py <file>` on the downloaded file. If it says LOW, look for a better photo in other articles on the same story (club site, ESPN, BBC, Sky Sports, agencies). Use a LOW photo only if nothing better exists after trying at least 3 sources, and say so in your report.
- Look at it before posting. It must fit the story and show the right person or club. Reject watermarks, other channels' logos, finished graphics or posters with text, screenshots, collages, and photos with the opponent as the main subject of a Chelsea or Como story.

# Como news posts

Before deciding to post nothing on @FComo1907, really look: run at least 4 web searches, including Como's youth team (Primavera, U19), Fabregas' latest words, Como transfer news, and Italian local press. Deciding from the channel's history alone is not allowed. Posting nothing is right only if those searches found nothing worthwhile.

To count today's @FComo1907 posts: recent_web.py shows UTC times and a Moscow day starts at 21:00 UTC of the previous date. Count only posts after that time, by their timestamps, not by post numbers.

# @FComo1907 writing style

Before writing any @FComo1907 caption, read `data/como_style.md` and write like those posts: very short, in a fan's voice. It overrides the format in a task.

# No repeated news (both channels)

The owner does not want the same news twice. Read `python recent_web.py 300 CHELSI_CHELSEAUZ_CFCUZ` for Chelsea or `python recent_web.py 100` for Como before choosing a story. Don't post a story or angle already covered in the last 14 days, by anyone, even in other words. Only a genuinely new fact justifies a new post, and then the post says only that new fact.

A fact counts as already posted if it appears anywhere in a channel post, including in the middle or at the end of a post about something else, by anyone. recent_web.py prints the full text of each post. Before you write, take the names and the key fact of your story and search for them, for example `python recent_web.py 100 | grep -i "камельо"`. If the fact is there, don't post it and don't repeat it inside a new post on another subject either: a new post must not re-tell facts the channel already gave.

# CHELSEA UZ sources

The owner wants more than ESPN. ESPN is for checking scores, fixtures and the table in the background. Don't build a post from ESPN data or name ESPN as the source, unless it is ESPN's own exclusive report. Never write «ESPN ma'lumotlari». Statistics come from English sources that published them (Opta, Squawka, WhoScored, Sofascore, FotMob, premierleague.com, The Athletic, BBC Sport, Sky Sports), named in the source line. If no English source has the number, don't post it.

# CHELSEA UZ history posts

The owner doesn't want minor #Kun_tarixi posts (2 Nov 2026, about post 4445: an ordinary 1:0 league win a year ago, «aytarli voqea emas»). Post #Kun_tarixi only for a really memorable moment: a trophy or a final, a club record, a legend's debut or farewell, a famous win that fans still talk about. An ordinary league match, however recent, is never one. If today has no such moment, choose another topic.

- News: start with @CFC_ChelseaFC, then chelseafc.com, Fabrizio Romano, David Ornstein and The Athletic (Simon Johnson, Liam Twomey), BBC Sport (Nizaar Kinsella), Telegraph (Matt Law), Sky Sports, Daily Mail (Kieran Gill), Standard Sport (Sam Tabuteau), Football London (Bobby Vincent), Guardian, talkSPORT (Ben Jacobs).
- Statistics: Opta, WhoScored, Sofascore, FotMob, Squawka, premierleague.com. Name the one you used.
- Check the last 10 channel posts and pick a different source from the ones they name when the story allows it. Never change or invent a source to get variety: name the source you really used.
