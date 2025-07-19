from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import random
from telegram import InputMediaPhoto, Poll
import asyncio
from telegram.ext import PollAnswerHandler
from datetime import datetime
import json
import os
from lang import tr
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

def language_keyboard():
    keyboard = [["Українська 🇺🇦", "English 🇬🇧"]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)








# Temporary in-memory storage
submitted_photos = []
waiting_for_photo = set()  # stores user_ids who are about to submit
user_points = {}       # maps user_id to points
waiting_for_photo = set()  # set of user_ids who used /submit
poll_buffers = {}  # user_id -> list of photo file_ids
waiting_for_poll_photos = set()  # user_ids currently uploading photos
all_users = set()
seen_photos = {}       # user_id -> set of message_ids they've seen via /feed
commented_photos = {}  # user_id -> set of message_ids they've commented on
poll_groups = []  # List of poll submissions, each as a dict: {user_id, photo_ids, poll_message_id, options, votes}
last_announcement_count = 0
votes_received = {}     # user_id -> int
comments_received = {}  # user_id -> int
celebrity_match_buffer = {}  # user_id -> list of photo file_ids
CELEBRITY_PRICE = 10  # ₴
MONOBANK_LINK = "https://send.monobank.ua/jar/mvaEKosuB"  # Replace with your link
paid_users = set()



DATA_FILE = 'data.json'

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({
            'user_points': user_points,
            'submitted_photos': submitted_photos,
            'poll_groups': poll_groups,
            'paid_users': list(paid_users),
            'banned_users': list(banned_users),
            'seen_photos': {k: list(v) for k, v in seen_photos.items()},
            'commented_photos': {k: list(v) for k, v in commented_photos.items()}
        }, f, default=str)

def load_data():
    if not os.path.exists(DATA_FILE):
        return

    global user_points, submitted_photos, poll_groups, paid_users, banned_users, seen_photos, commented_photos

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
        user_points = data.get('user_points', {})
        submitted_photos = data.get('submitted_photos', [])
        poll_groups = data.get('poll_groups', [])
        paid_users = set(data.get('paid_users', []))
        banned_users = set(data.get('banned_users', []))
        seen_photos = {int(k): set(v) for k, v in data.get('seen_photos', {}).items()}
        commented_photos = {int(k): set(v) for k, v in data.get('commented_photos', {}).items()}




async def handle_language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if "Українська" in text:
        context.user_data['lang'] = 'uk'
        lang = 'uk'
        await update.message.reply_text("✅ Мову змінено на українську! Введіть /start, щоб розпочати", reply_markup=ReplyKeyboardRemove())
    elif "English" in text:
        context.user_data['lang'] = 'en'
        lang = 'en'
        await update.message.reply_text("✅ Language set to English! Press /start to begin", reply_markup=ReplyKeyboardRemove())
    else:
        return

    # 🔓 Unban check (optional)
    if user_id in banned_users:
        await update.message.reply_text(tr(lang, 'banned'))
        return

    # ✅ Add user and give points
    all_users.add(user_id)
    if user_id not in user_points:
        user_points[user_id] = 50
        save_data()

    # ✅ Show welcome message
    name = update.effective_user.first_name
    await update.message.reply_text(tr(lang, 'start', name=name), parse_mode='Markdown')











import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = 924475051  # 👈 Replace with your actual Telegram user ID
banned_users = set()






# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'lang' not in context.user_data:
        keyboard = [["Українська 🇺🇦", "English 🇬🇧"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("🌐 Please choose your language:", reply_markup=reply_markup)
        return

    user_id = update.effective_user.id
    if user_id in banned_users:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'banned'))
        return

    all_users.add(user_id)

    # 🎁 Give 10 starting points if user is new
    if user_id not in user_points:
        user_points[user_id] = 50
        save_data()

    lang = context.user_data['lang']
    name = update.effective_user.first_name
    await update.message.reply_text(tr(lang, 'start', name=name))
   

# /submit
async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in banned_users:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'banned'))
        return

    points = user_points.get(user_id, 0)

    if points < 15:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'not_enough_points'))
        return

    waiting_for_photo.add(user_id)
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(tr(lang, 'submit_prompt'))

#points system
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.poll_answer.user.id
    poll_id = update.poll_answer.poll_id
    selected_options = update.poll_answer.option_ids

    lang = context.user_data.get('lang', 'en')
    print(tr(lang, 'poll_vote_received', poll_id=poll_id))

    user_points[user_id] = user_points.get(user_id, 0) + 1
    save_data()
    lang = context.user_data.get('lang', 'en')
    print(tr(lang, 'poll_point_earned', user_id=user_id))

    for poll in poll_groups:
        if poll.get('poll_id') == poll_id:
            owner_id = poll['user_id']
            options = poll['options']
            voter_name = update.effective_user.first_name

            lang = context.user_data.get('lang', 'en')
            print(tr(lang, 'matching_poll_found', owner_id=owner_id))

            poll['votes'][user_id] = selected_options
            
            vote_count = len(poll['votes'])

            # 👥 Track how many votes the owner received
            votes_received[owner_id] = votes_received.get(owner_id, 0) + 1

            # 🧮 Deduct 1 point for every 3 votes received
            if votes_received[owner_id] % 3 == 0:
                user_points[owner_id] = user_points.get(owner_id, 0) - 1
                lang = context.user_data.get('lang', 'en')
                await context.bot.send_message(
                    chat_id=owner_id,
                    text= tr(lang, 'poll_result_notice')
                )


            owner_points = user_points.get(owner_id, 0)

            # Notify the poll owner
            if vote_count == 1:
                lang = context.user_data.get('lang', 'en')
                await context.bot.send_message(
                    chat_id=owner_id,
                    text= tr(lang, 'poll_vote_notice')
                )

            elif vote_count % 10 == 0:
                lang = context.user_data.get('lang', 'en')
                await context.bot.send_message(
                    chat_id=owner_id,
                    text=tr(lang, 'poll_vote_count', vote_count=vote_count)
                )

            # Deduct 1 point from poll owner per vote
            if owner_points > 0:
                user_points[owner_id] -= 1
            else:
                lang = context.user_data.get('lang', 'en')
                await context.bot.send_message(
                    chat_id=owner_id,
                    text=tr(lang, 'voting_closed_no_points')    
                )

            lang = context.user_data.get('lang', 'en')
            voted_options = [options[i] for i in selected_options]
            result_text = tr(lang, 'poll_vote_details', voter_name=voter_name, options=', '.join(voted_options))

            try:
                await context.bot.send_message(
                    chat_id=poll['poll_chat_id'],
                    text=result_text,
                    reply_to_message_id=poll['poll_message_id']
                )
            except Exception as e:
                lang = context.user_data.get('lang', 'en')
                print(tr(lang, 'poll_notify_error', error=e))
            break



# handle actual photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file_id = photo.file_id

    # 👤 Check if user is submitting for celebrity match
    if context.user_data.get('waiting_for_celebrity'):
        if user_id not in paid_users:
            lang = context.user_data.get('lang', 'en')
            await update.message.reply_text(tr(lang, 'need_payment_confirmation'))
            return
        context.user_data['waiting_for_celebrity'] = False

        # Forward photo to admin
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_USER_ID,
                photo=update.message.photo[-1].file_id,
                caption=f"🌟 Celebrity Match request from user {update.effective_user.full_name} (ID: {user_id}).\nReply to this photo with your answer."
            )

            lang = context.user_data.get('lang', 'en')
            await update.message.reply_text(
                tr(lang, 'photo_received_expert_review')
            )
        except Exception as e:
            lang = context.user_data.get('lang', 'en')
            await update.message.reply_text(tr(lang, 'photo_send_failed'))
            print(tr(lang, 'photo_forward_error_log', error=e))


        return

    # 🧠 If this is a /pollme photo upload:
    if user_id in waiting_for_poll_photos:
        if user_id not in poll_buffers:
            poll_buffers[user_id] = []

        if len(poll_buffers[user_id]) >= 10:
            lang = context.user_data.get('lang', 'en')
            await update.message.reply_text(tr(lang, 'max_photos_uploaded'))
            return

        poll_buffers[user_id].append(file_id)
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(
            tr(lang, 'poll_photo_saved', num=len(poll_buffers[user_id]))
        )
        return

    # 🧠 If this is a normal /submit flow:
    if user_id not in waiting_for_photo:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'please_use_submit'))
        return

    waiting_for_photo.remove(user_id)

    message_id = update.message.message_id

    caption = update.message.caption or ""


    submitted_photos.append({
        'file_id': file_id,
        'user_id': user_id,
        'message_id': message_id,
        'chat_id': update.message.chat_id,
        'is_poll': False,
        'caption': caption,
        'timestamp': datetime.now()
    })
    save_data()

    # Notify all users when milestone is reached
    global last_announcement_count
    photo_count = len(submitted_photos)

    if photo_count % 10 == 0 and photo_count != last_announcement_count:
        last_announcement_count = photo_count
        for uid in all_users:
            try:
                lang = context.user_data.get('lang', 'en')
                await context.bot.send_message(
                    chat_id=uid,
                    text=tr(lang, 'new_photos_feed_notify', photo_count=photo_count)
                )
                
            except Exception as e:
                lang = context.user_data.get('lang', 'en')
                print(tr(lang, 'notify_user_error_log', uid=uid, error=e))


    user_points[user_id] = user_points.get(user_id, 0) - 15
    save_data()
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(tr(lang, 'photo_submitted'))

    



#Handle poll questions
async def handle_poll_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in waiting_for_poll_photos:
        context.user_data[f'poll_question_{user_id}'] = update.message.text
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'poll_question_saved'))


#track replies
async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message is None:
        return  # Not a reply

    replying_user_id = update.effective_user.id
    target_message_id = update.message.reply_to_message.message_id

    # Check if already replied to this specific message
    commented_photos.setdefault(replying_user_id, set())
    
    # Get file_id of the replied-to message
    photo_files = context.bot_data.get('photo_files', {})
    file_id = photo_files.get(target_message_id)

    if not file_id:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'reply_no_match'))
        return
    
    if file_id in commented_photos[replying_user_id]:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'already_commented'))
        return


    # Get photo uploader
    photo_links = context.bot_data.get('photo_links', {})
    uploader_id = photo_links.get(target_message_id)

    if uploader_id is None:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'reply_no_match'))
        return

    if replying_user_id == uploader_id:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'comment_own_photo'))
        return

    # Mark this message as reviewed
    commented_photos[replying_user_id].add(file_id)

    # Award points
    user_points[replying_user_id] = user_points.get(replying_user_id, 0) + 2
    save_data()
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(
        tr(lang, 'comment_points_awarded', points=user_points[replying_user_id])
    )
    save_data()

    # Get file_id of the photo being replied to
    photo_files = context.bot_data.get('photo_files', {})
    file_id = photo_files.get(target_message_id)

    # Send the photo and comment back to the original uploader
    try:
        lang = context.user_data.get('lang', 'en')
        await context.bot.send_photo(
            chat_id=uploader_id,
            photo=file_id,
            caption=tr(lang, 'photo_reply_notification', comment=update.message.text)
        )
    except Exception as e:
        lang = context.user_data.get('lang', 'en')
        print(tr(lang, 'notify_uploader_error_log', error=e))

    # 👥 Track comments received
    comments_received[uploader_id] = comments_received.get(uploader_id, 0) + 1

    # 🧮 Deduct 1 point for every 3 comments received
    if comments_received[uploader_id] % 3 == 0:
        user_points[uploader_id] = user_points.get(uploader_id, 0) - 1
        save_data()
        lang = context.user_data.get('lang', 'en')
        await context.bot.send_message(
            chat_id=uploader_id,
            text = tr(lang, 'comment_notification')
        )
        save_data()

    # Show next unseen photo
    unseen_photos = [
        photo for photo in submitted_photos
        if photo['user_id'] != replying_user_id and photo['message_id'] not in seen_photos[replying_user_id]
    ]

    if unseen_photos:
        next_photo = random.choice(unseen_photos)
        lang = context.user_data.get('lang', 'en')
        caption = tr(lang, 'feed_photo_caption')
        new_message = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=next_photo['file_id'],
            caption=caption
        )
        context.bot_data.setdefault('photo_links', {})[new_message.message_id] = next_photo['user_id']
        context.bot_data.setdefault('photo_files', {})[new_message.message_id] = next_photo['file_id']
        seen_photos.setdefault(replying_user_id, set()).add(new_message.message_id)
    else:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'no_more_photos'))

    # Prevent replies to polls
    if update.message.reply_to_message.poll:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'no_comment_on_poll'))
        return






#feed function
async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in banned_users:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'banned'))
        return

    seen_ids = seen_photos.get(user_id, set())
    photo_links = context.bot_data.setdefault('photo_links', {})
    photo_files = context.bot_data.setdefault('photo_files', {})

    if not submitted_photos and not poll_groups:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'no_photos_submitted'))
        return

    # 👉 Add this right after the check
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(tr(lang, 'feed_instructions'))

    # Only show photos not submitted by the user and not seen before (by file_id)
    unseen_photos = []

    seen_file_ids = seen_photos.get(user_id, set())

    for photo in submitted_photos:
        if photo['user_id'] == user_id:
            continue  # Don’t show user their own photo

        if photo['file_id'] in seen_photos.get(user_id, set()):
            continue

        if photo['file_id'] in commented_photos.get(user_id, set()):
            continue

        unseen_photos.append(photo)

    unseen_polls = [
        poll for poll in poll_groups
        if poll['user_id'] != user_id and poll.get('poll_message_id') not in seen_photos.get(user_id, set())
    ]

    if not unseen_photos and not unseen_polls:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'all_photos_seen'))
        return

    if unseen_photos and (not unseen_polls or random.choice([True, False])):
        # Show a regular photo
        photo = random.choice(unseen_photos)

        lang = context.user_data.get('lang', 'en')
        caption = photo.get('caption', '')
        feedback_prompt = tr(lang, 'photo_feedback_prompt')
        final_caption = f"{caption}\n\n{feedback_prompt}" if caption else feedback_prompt

        sent_message = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo['file_id'],
            caption=final_caption
        )

        # ✅ Mark photo as seen using file_id
        seen_photos.setdefault(user_id, set()).update({
            photo['file_id'],
            sent_message.message_id
        })
        save_data()

        # ✅ Also mark the message ID (for reply tracking)
        seen_photos.setdefault(user_id, set()).add(sent_message.message_id)




        # Save mapping for reply tracking
        photo_links[sent_message.message_id] = photo['user_id']
        photo_files[sent_message.message_id] = photo['file_id']

    else:
        # Show a poll group
        poll = random.choice(unseen_polls)

        # Step 1: show the media group
        await context.bot.send_media_group(
            chat_id=update.effective_chat.id, 
            media=[InputMediaPhoto(pid) for pid in poll['photo_ids']]
        )

        # Step 2: forward the original poll
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=poll['poll_chat_id'],
            message_id=poll['poll_message_id']
        )

        lang = context.user_data.get('lang', 'en')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=tr(lang, 'poll_voted_press_feed')
        )

        # Step 3: mark as seen
        seen_photos.setdefault(user_id, set()).add(poll['poll_message_id'])
        save_data()

        return  # 🚨 prevent rest of the function from trying to access sent_message (photo)

    # Save mapping of this new message
    photo_links[sent_message.message_id] = photo['user_id']
    photo_files[sent_message.message_id] = photo['file_id']

    seen_photos.setdefault(user_id, set()).add(sent_message.message_id)









#points
async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in banned_users:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'banned'))
        return

    points = user_points.get(user_id, 0)
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(tr(lang, 'points', points=points))

#poll command
async def pollme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in banned_users:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'banned'))
        return

    points = user_points.get(user_id, 0)

    if points < 15:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(
            tr(lang, 'not_enough_points')
        )
        return

    poll_buffers[user_id] = []
    waiting_for_poll_photos.add(user_id)
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(tr(lang, 'poll_photo_instructions'))

#donepoll
async def donepoll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in banned_users:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'banned'))
        return

    if user_points.get(user_id, 0) < 15:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'not_enough_points_poll'))
        return

    if user_id not in poll_buffers or not poll_buffers[user_id]:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'no_photos_submitted'))
        return

    waiting_for_poll_photos.discard(user_id)
    photo_ids = poll_buffers[user_id]

    # Store poll group (instead of adding photos to submitted_photos one-by-one)
    poll_groups.append({
        'user_id': user_id,
        'photo_ids': photo_ids,
        'poll_message_id': None,  # will be filled below
        'poll_chat_id': update.effective_chat.id,
        'options': [f"Photo {i+1}" for i in range(len(photo_ids))],
        'votes': {},
        'timestamp': datetime.now()
    })


    # ✅ Show user's question before the photos, if provided
    question_text = context.user_data.get(f'poll_question_{user_id}', "")

    # Step 1: Send album of photos
    media_group = [InputMediaPhoto(photo_id) for photo_id in photo_ids]
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)

    # Step 2: Prepare poll options
    options = [f"Photo {i+1}" for i in range(len(photo_ids))]

    # Step 3: Send anonymous poll
    custom_question = context.user_data.get(f'poll_question_{user_id}').strip()
    if not custom_question:
        custom_question = tr(lang, 'poll_question')  # fallback to default

    poll_message = await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=custom_question[:300],  # Telegram poll question max length = 300
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True
    )

    poll_groups[-1]['poll_id'] = poll_message.poll.id
    poll_groups[-1]['poll_message_id'] = poll_message.message_id

    user_points[user_id] = user_points.get(user_id, 0) - 15
    save_data()
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(tr(lang, 'poll_sent'))

    # Save poll for future logic
    context.bot_data['current_poll'] = {
        'message_id': poll_message.message_id,
        'chat_id': poll_message.chat.id,
        'owner_id': user_id,
        'photo_ids': photo_ids,
        'options': options,
        'votes': {},
        'eligible_voters': []
    }

    import random

    # Randomly shuffle voters
    random.shuffle(available_voters)
    selected_voters = available_voters[:owner_points]

    context.bot_data['current_poll']['eligible_voters'] = selected_voters

    # Schedule voter invitations (one at a time)
    for voter_id in selected_voters:
        context.job_queue.run_once(
            send_poll_to_voter,
            when=0,  # Send immediately (can stagger if needed)
            data={
                'voter_id': voter_id,
                'poll_message_id': poll_message.message_id,
                'poll_chat_id': poll_message.chat.id,
                'owner_id': user_id
            }
        )

async def send_poll_to_voter(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    voter_id = job_data['voter_id']
    poll_message_id = job_data['poll_message_id']
    poll_chat_id = job_data['poll_chat_id']
    owner_id = job_data['owner_id']

    try:
        await context.bot.forward_message(
            chat_id=voter_id,
            from_chat_id=poll_chat_id,
            message_id=poll_message_id
        )
        lang = context.user_data.get('lang', 'en')
        await context.bot.send_message(voter_id, tr(lang, 'please_vote'))
    except:
        # If the user has blocked the bot or it can't message them
        lang = context.user_data.get('lang', 'en')
        await context.bot.send_message(owner_id, tr(lang, 'poll_send_fail', voter_id=voter_id))


#Delete function
async def delete_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    latest_photo = None
    latest_poll = None

    # Find user's latest photo
    for photo in reversed(submitted_photos):
        if photo['user_id'] == user_id:
            latest_photo = photo
            break

    # Find user's latest poll
    for poll in reversed(poll_groups):
        if poll['user_id'] == user_id:
            latest_poll = poll
            break

    # Compare timestamps
    if latest_photo and (not latest_poll or latest_photo['timestamp'] > latest_poll['timestamp']):
        submitted_photos.remove(latest_photo)
        save_data()
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'last_photo_deleted'))
    elif latest_poll:
        poll_groups.remove(latest_poll)
        save_data()
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'last_poll_deleted'))
    else:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'nothing_to_delete'))




#Delete all
async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Delete all submitted photos by the user
    before_photos = len(submitted_photos)
    submitted_photos[:] = [p for p in submitted_photos if p['user_id'] != user_id]
    deleted_photos = before_photos - len(submitted_photos)

    # Delete all polls by the user
    before_polls = len(poll_groups)
    poll_groups[:] = [p for p in poll_groups if p['user_id'] != user_id]
    save_data()
    deleted_polls = before_polls - len(poll_groups)

    if deleted_photos == 0 and deleted_polls == 0:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'nothing_found_to_delete'))
    else:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'deleted_all', deleted_photos=deleted_photos, deleted_polls=deleted_polls))

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message is None:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'report_reply_required'))
        return

    target_message = update.message.reply_to_message
    reporter_id = update.effective_user.id

    try:
        # Forward the reported message to admin
        await context.bot.forward_message(
            chat_id=ADMIN_USER_ID,
            from_chat_id=target_message.chat_id,
            message_id=target_message.message_id
        )

        # Notify admin who reported
        await context.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=f"🚨 User {reporter_id} reported a photo."
        )

        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'report_received'))
    except Exception as e:
        lang = context.user_data.get('lang', 'en')
        print(tr(lang, 'report_forward_fail', error=e))
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'report_failed'))



#Banned users
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("🚫 You are not allowed to use this command.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: /ban_user <user_id>")
        return

    try:
        target_id = int(context.args[0])
        banned_users.add(target_id)
        save_data()
        await update.message.reply_text(f"🚫 User {target_id} has been banned from the bot.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Please provide a number.")


#celebrity
async def celebrity_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in paid_users:
        context.user_data['waiting_for_celebrity'] = True
        celebrity_match_buffer[user_id] = []
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'payment_already_confirmed'))
    else:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(
            tr(lang, 'celebrity_intro', price=CELEBRITY_PRICE, link=MONOBANK_LINK)
        )



#Admin reply celebrity
async def handle_admin_celebrity_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        return  # Not admin

    if update.message.reply_to_message is None:
        return  # Not replying

    caption = update.message.reply_to_message.caption
    if caption and "Celebrity Match request from user" in caption:
        # Extract user ID from caption
        try:
            user_id_line = caption.split("ID: ")[1]
            user_id = int(user_id_line.strip().split(")")[0])

            lang = context.user_data.get('lang', 'en')
            await context.bot.send_message(
                chat_id=user_id,
                text=tr(lang, 'celebrity_result', result=update.message.text)
            )

            await update.message.reply_text("✅ Sent to user!")
        except Exception as e:
            await update.message.reply_text("❌ Failed to parse or send.")
            print(f"Error replying to celebrity match: {e}")



async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in paid_users:
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'payment_already_confirmed'))
        return

    paid_users.add(user_id)
    save_data()
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(tr(lang, 'paid_confirmed'))


# /add_points <user_id> <amount>
async def add_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("🚫 You are not allowed to use this command.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Usage: /add_points <user_id> <amount>")
        return

    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])

        user_points[target_id] = user_points.get(target_id, 0) + amount
        save_data()

        await update.message.reply_text(
            f"✅ Added {amount} point(s) to user {target_id}. New total: {user_points[target_id]}"
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid arguments. Please provide numbers only.")


async def handle_all_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Admin replying to celebrity match
    if (
        update.effective_user.id == ADMIN_USER_ID and
        update.message.reply_to_message and
        update.message.reply_to_message.caption and
        "Celebrity Match request from user" in update.message.reply_to_message.caption
    ):
        await handle_admin_celebrity_reply(update, context)
        return

    # Everyone else – process regular photo replies
    await handle_reply(update, context)


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(
        tr(lang, 'help_message'),
        parse_mode='Markdown'
    )



async def buy_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(
        tr(lang, 'buy_points'),
        parse_mode='Markdown'
    )





# New command: /language
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Українська 🇺🇦", "English 🇬🇧"]]
    await update.message.reply_text(
        "🌐 Please choose your language:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # 🌐 Language selection
    if "Українська" in text or "English" in text:
        await handle_language_choice(update, context)
        return

    # 📊 Poll question input
    if user_id in waiting_for_poll_photos:
        context.user_data[f'poll_question_{user_id}'] = text
        lang = context.user_data.get('lang', 'en')
        await update.message.reply_text(tr(lang, 'poll_question_saved'))
        return

    # ❓ Otherwise, ignore or log unhandled text
    return



# launch the bot
if __name__ == '__main__':
    load_data()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('submit', submit))
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_all_replies))
    app.add_handler(CommandHandler('feed', feed))
    app.add_handler(CommandHandler('points', points))
    app.add_handler(CommandHandler('pollme', pollme))
    app.add_handler(CommandHandler('donepoll', donepoll))
    app.add_handler(CommandHandler('delete_last', delete_last))
    app.add_handler(CommandHandler('delete_all', delete_all))
    app.add_handler(CommandHandler('report', report))
    app.add_handler(CommandHandler('ban_user', ban_user))
    app.add_handler(CommandHandler('celebrity_match', celebrity_match))
    app.add_handler(CommandHandler('paid', paid))
    app.add_handler(CommandHandler('add_points', add_points))
    app.add_handler(CommandHandler('rules', rules))
    app.add_handler(CommandHandler('buy_points', buy_points))
    app.add_handler(CommandHandler('language', choose_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.REPLY, handle_text))

    print("Bot is running...")
    app.run_polling()