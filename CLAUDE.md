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

# CHELSEA UZ post rules (owner, 4 Nov 2026)

These override the task prompt and data/emoji_guide_chelsea.md where they differ.

- Only fresh news. A news post is about something published in the last 24 hours and not yet in the channel. Never present an old story as news and never re-tell earlier news. If nothing fresh and new is found after a real search, post nothing and say so in the report: this replaces "Nothing to post is not acceptable".
- History is allowed only as clearly labelled history, at most one post a day, and only for a really memorable moment: a legend, a trophy or final, a historic win, a club record. An ordinary league match is never history (the owner rejected post 4445 about a 1:0 win a year ago).
- No headline. The post starts straight with the news itself, not with a bold title line or a title ending in a colon. Interviews too: one short sentence saying who said it and when, then the quote. The stickers stay on the first line as before.
- Don't translate word for word. Say the point in your own short, clear Uzbek: usually 2 or 3 short sentences. For an interview, give only the one or two most interesting quotes, shortened, not the whole press conference.
- Mainly English sources: the club, English journalists and outlets (The Athletic, BBC, Sky Sports, Telegraph, Daily Mail, Standard, Football London, Guardian, talkSPORT, Fabrizio Romano, Ben Jacobs). Use other sources only when an English one doesn't have the story.

# CHELSEA UZ sources and topics (owner's list, 4 Nov 2026)

1. Main source, use first: the club, @ChelseaFC on X and the Telegram channel @CFC_ChelseaFC. Club news, players' condition, interviews and full press conferences, training, club photos.
2. Trusted journalists and outlets for club and transfer news: Fabrizio Romano (transfers); David Ornstein, Simon Johnson, Liam Twomey (The Athletic); Ben Jacobs, Alex Crook (talkSPORT); Nizaar Kinsella (BBC Sport); Kieran Gill (Daily Mail); Matt Law (Telegraph); Bobby Vincent (Football London); Dom Smith, Sam Tabuteau (Standard Sport); the Guardian. Data and kits: Transfermarkt, Footy Headlines, WhoScored, Opta and Opta Analyst, Sofascore, Squawka, FotMob, LiveScore.
3. Telegram channels, read with `python recent_web.py 30 <name>`: ChelseaSunSport, CFC_ChelseaFC, Chelsea_fc_worldwide, news_blues, breakevens, beautyCFC, tg_chelsea_news, cfc_london. Apart from CFC_ChelseaFC these are fan channels: use them to find stories, then confirm the story with the club or a journalist from point 2 and name that source, not the fan channel. Don't take their photos if they carry their logo or watermark.
4. Topics: pre-match (squad, press conference, the coach's words, the opponent); match analysis (result, player ratings, key statistics, records); transfer analysis (fee, contract length, stage of talks, not only who comes or goes); club history (as limited above); the academy (youth results, promotions to the first team, loan players).
5. The owner's nine rules: never post the same news twice; check every item's date and time; never give old news as new; never present a journalist's guess as official; injuries only from reliable sources; players' names in their original English spelling; natural Uzbek, not word for word; check the facts before every post; important unconfirmed news goes to the admin for approval (Saved Messages), not to the channel.

# Too many runs posted nothing (4 Nov 2026): what counts as postable

The owner asked why posts stopped. Skipping is only right when there is truly nothing. These also count as fresh posts, and override the task prompts of both channels:

- CHELSEA UZ: a report by one tier-1 journalist (Romano, Ornstein, Johnson, Twomey, Jacobs, Crook, Kinsella, Gill, Law, Vincent, Smith, Tabuteau) is enough for a post, written as their report («... ma'lumotiga ko'ra»). Don't wait for a second source for that. Only important unconfirmed news goes to the admin (rule 9).
- CHELSEA UZ: the club's own posts of the last 24 hours (@ChelseaFC, @CFC_ChelseaFC): training photos, player Instagram posts, club statistics, videos. The owner listed training and club photos as main content. A short post with the photo and one or two sentences is fine.
- @FComo1907: on a match day and the day before, everything about that match counts as fresh until kickoff, including the press conference of the day before, the convocati, the opponent, the referee, the fans' trip. Fresh otherwise means the last 24 hours, not 12.
- Both: a missing photo of the person is not a reason to skip. Use the photo of the source article, or a recent team or club photo from this season (club site, the source's article, the club's Telegram channel). Only skip when no fitting photo from this season exists at all.

# CHELSEA UZ topic mix (owner, 4 Nov 2026)

"Faqat transfer emas, boshqa mavzularda ham". Vary the topics through the day: at most one transfer post in every three, and never two transfer posts in a row. Before choosing, look at the last 5 channel posts and pick a different topic from the owner's list: club news and training, players' condition and injuries, interviews and press conferences, pre-match, match analysis and ratings, statistics, the academy and loan players, Chelsea Women, a memorable history moment.

# @FComo1907 pause (owner, 5 Nov 2026)

«До 15 МСК ничего не выкладывай, потом начинай работу». Before 2026-11-05 12:00 UTC (15:00 по МСК) post nothing on @FComo1907: end the run at once and report the pause. From 12:00 UTC work normally.

# @FComo1907: post on every run (owner, 6 Nov 2026)

The owner asked why the Como channel isn't working: since the pause ended, every run posted nothing after a minute of searching. This overrides "posting nothing is fine" in the task: each run publishes ONE post, unless the day's limit is reached or it is the match blackout.

- Search properly, not only WebSearch (it is US-based and returns old pages). Open these pages directly with WebFetch or curl and read today's items with their times: https://www.tuttomercatoweb.com/como/ , https://www.calciomercato.com/squadre/como , https://www.laprovinciadicomo.it/sport/calcio/como-calcio/ , https://www.calciocomo1907.it/ , https://comofootball.com/en/news/ , and https://t.me/s/<name> of Italian or Russian Como channels.
- Postable when there is no hard news: an Italian journalist's or paper's opinion about a Como player or transfer, written as their view («TMW считает…», «в Италии пишут…»); a player's quote from an interview; a training or club photo of the last 24 hours with one line; a short fan question that invites comments («Кого бы вы поставили вместо Кина?»); a number with a real point. Rumours and opinions are fine when they are attributed and not yet in the channel.
- Still never repeat a story or angle already in the channel, never write AI filler, keep the admins' short fan style (data/como_style.md).

# @FComo1907 stickers: no faces, flags for players (owner, 7 Nov 2026)

The owner: «yuz stikerlaridan foydalanma, o'yinchi bo'lsa qaysi millatdan bo'lsa o'sha millat bayrog'ini qo'y». The custom emoji 5226842334418736150 is a player's face, not a ball: never use it, nor any other face or portrait sticker, on @FComo1907. This overrides the sticker list in the task.
- A post about a player: the plain flag of his country first, e.g. 🇦🇷 Нико Пас, 🇬🇷 Дувикас, 🇭🇷 Батурина, 🇪🇸 Фабрегас. Check the nationality in a source if unsure.
- A general football line: plain ⚽️ (Unicode, not a custom emoji). The other custom stickers in the task (💼 ✅ ❌ 🏥 💰 📰) and the 🇮🇹 crest signature stay.

# @FComo1907 matchday 8 Nov 2026: use the owner's poster

The owner approved a ready poster for «Интер» — «Комо» (8 Nov 2026, 20:00 МСК). In the match-day run on 8 Nov 2026, do NOT render a poster: copy assets/como/matchday_2026-11-08.png to outbox/$TS.png and publish it with exactly this caption (do everything else the task asks, such as the match metadata file, as usual):

Матчдэй!

«Интер» — «Комо»
Серия А, 11 тур
20:00 по МСК, «Сан-Сиро»

<tg-emoji emoji-id="5229073990835804268">🇮🇹</tg-emoji> @FComo1907

# @FComo1907: transfer news only (owner, 9 Nov 2026)

«Комо uchun faqat transfer yangiliklar qo'y». This overrides every earlier @FComo1907 news rule above, including "post on every run" and the match-day and other topics in the task.
- The news task posts ONLY transfer news: players Como wants, bids, talks, fees, contracts and renewals, Como players wanted by other clubs, loans, departures. Rumours are fine when attributed («Николо Скира пишет…»).
- No other topics in the news task: no match previews or reactions, no national teams, no opinions, quotes, history, youth or women's team, fan questions.
- If there is no fresh transfer story (last 24 hours, not yet in the channel), post nothing.
- Unchanged: the matchday poster, live commentary and result poster automations; the style, sticker and no-repeat rules.

# @FComo1907: a transfer post every 2 hours (owner, 10 Nov 2026)

«Каждые 2 часа Комо каналига трансфер янгилик кой». This overrides "if there is no fresh transfer story, post nothing" above: every news run publishes ONE transfer post (only the match blackout stops it).
- First choice: transfer news of the last 24 hours not yet in the channel.
- If there is none, use transfer material of the last 7 days that the channel hasn't covered, or a transfer angle the channel hasn't given yet: a Como player's contract situation or release clause, his market value (Transfermarkt), which clubs follow him and why, a Como target's numbers this season, what an Italian journalist or paper writes about Como's January or summer plans, a loan player's progress with an eye on his future.
- Still transfers only, still no repeats (check `python recent_web.py 100` and grep names), rumours attributed, facts checked, the admins' short style, a flag for the player's nationality, no face stickers.
