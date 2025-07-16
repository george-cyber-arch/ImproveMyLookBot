from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import random
from telegram import InputMediaPhoto, Poll
import asyncio
from telegram.ext import PollAnswerHandler

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



import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    all_users.add(user_id)

    # 🎁 Give 10 starting points if user is new
    if user_id not in user_points:
        user_points[user_id] = 10

    await update.message.reply_text(
        f"👋 Hello, {update.effective_user.first_name}!\n"
        f"🏁 You start with 10 points.\n"
        f"Use /submit or /pollme to get feedback.\n"
        f"Use /feed to rate others and earn more!"
    )

# /submit
async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    waiting_for_photo.add(user_id)
    await update.message.reply_text("Please send me a photo you'd like to submit.")

#points system
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.poll_answer.user.id
    poll_id = update.poll_answer.poll_id
    selected_options = update.poll_answer.option_ids

    user_points[user_id] = user_points.get(user_id, 0) + 1
    print(f"✅ {user_id} voted in a poll and earned 1 point.")

    for poll in poll_groups:
        if poll.get('poll_id') == poll_id:
            owner_id = poll['user_id']
            options = poll['options']

            # ✅ Block changing vote: only accept first submission
            if user_id in poll['votes']:
                print(f"⛔ {user_id} already voted in this poll. Ignoring vote change.")
                return  # Do not allow vote retraction/change

            poll['votes'][user_id] = selected_options

            poll['vote_count'] = poll.get('vote_count', 0) + 1
            uploader_points = user_points.get(owner_id, 0)

            if poll['vote_count'] == uploader_points:
                try:
                    await context.bot.send_message(
                        chat_id=owner_id,
                        text="📭 Your poll has received the maximum number of votes based on your current points.\nUse /feed to earn more!"
                    )

                except Exception as e:
                    print(f"❌ Could not notify poll owner of limit: {e}")

            vote_count = len(poll['votes'])

            if vote_count == 1:
                try:
                    await context.bot.send_message(
                        chat_id=owner_id,
                        text="🎉 Your poll just received its first vote!"
                    )
                except Exception as e:
                    print(f"❌ Could not send first vote notification: {e}")

            vote_count = len(poll['votes'])
            last_notified = poll.get('notified_count', 0)

            # Check if we crossed a multiple of 5
            if vote_count >= last_notified + 5:
                poll['notified_count'] = vote_count  # update milestone

            try:
                await context.bot.send_message(
                    chat_id=owner_id,
                    text=f"📊 Your poll has received {vote_count} votes so far!"
                )
            except Exception as e:
                print(f"❌ Could not send vote milestone to poll owner: {e}")

            voted_options = [options[i] for i in selected_options]


    # Show next item in feed for the voter
    await feed_from_poll_vote(context, user_id)





# handle actual photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file_id = photo.file_id

    # 🧠 If this is a /pollme photo upload:
    if user_id in waiting_for_poll_photos:
        if user_id not in poll_buffers:
            poll_buffers[user_id] = []

        if len(poll_buffers[user_id]) >= 10:
            await update.message.reply_text("❌ You already uploaded 10 photos. Send /donepoll to proceed.")
            return

        poll_buffers[user_id].append(file_id)
        await update.message.reply_text(f"✅ Photo {len(poll_buffers[user_id])} saved for poll.")
        return

    # 🧠 If this is a normal /submit flow:
    if user_id not in waiting_for_photo:
        await update.message.reply_text("⚠️ Please use /submit before sending a photo.")
        return

    waiting_for_photo.remove(user_id)

    message_id = update.message.message_id

    submitted_photos.append({
    'file_id': file_id,
    'user_id': user_id,
    'message_id': message_id,
    'chat_id': update.message.chat_id,
    'is_poll': False,
    'comments': 0
 })

    user_points[user_id] = user_points.get(user_id, 0) - 1
    await update.message.reply_text("✅ Your photo has been submitted!")

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
        await update.message.reply_text("❌ This reply doesn't match any submitted photo.")
        return
    
    if file_id in commented_photos[replying_user_id]:
        await update.message.reply_text("⚠️ You already commented on this photo. Here's another one...")

        # 👇 Trigger next photo from feed
        dummy_update = Update(update_id=0, message=None)

        class DummyMessage:
            def __init__(self, user_id, chat_id):
                self.from_user = type("User", (), {"id": user_id})
                self.chat = type("Chat", (), {"id": chat_id})
                self.chat_id = chat_id
                self.message_id = 0

        dummy_update.effective_user = update.effective_user
        dummy_update.effective_chat = update.effective_chat
        dummy_update.message = DummyMessage(replying_user_id, update.effective_chat.id)

        await feed(dummy_update, context)
        return


    # Get photo uploader
    photo_links = context.bot_data.get('photo_links', {})
    uploader_id = photo_links.get(target_message_id)

    if uploader_id is None:
        await update.message.reply_text("❌ This reply doesn't match any submitted photo.")
        return

    if replying_user_id == uploader_id:
        await update.message.reply_text("🤔 You can’t comment on your own photo.")
        return

    # Mark this message as reviewed
    commented_photos[replying_user_id].add(file_id)

    # Award points
    user_points[replying_user_id] = user_points.get(replying_user_id, 0) + 2
    await update.message.reply_text(
        f"💬 You earned 2 points for commenting! Total: {user_points[replying_user_id]}"
    )

    # Get file_id of the photo being replied to
    photo_files = context.bot_data.get('photo_files', {})
    file_id = photo_files.get(target_message_id)

    # Send the photo and comment back to the original uploader
    try:
        await context.bot.send_photo(
            chat_id=uploader_id,
            photo=file_id,
            caption=f"💬 Someone replied to your photo:\n\"{update.message.text}\""
        )

        # Increase comment count for that photo
        for photo in submitted_photos:
            if photo['file_id'] == file_id:
                photo['comments'] = photo.get('comments', 0) + 1
                uploader_points = user_points.get(photo['user_id'], 0)

                if photo['comments'] >= uploader_points:
                    await context.bot.send_message(
                        chat_id=photo['user_id'],
                        text="📭 Your photo has reached its feedback limit.\nUse /feed to earn more points and receive more comments."
                    )
                break             
    except Exception as e:
        print(f"❌ Could not notify uploader: {e}")

    # Show next unseen photo
    unseen_photos = [
        photo for photo in submitted_photos
        if photo['user_id'] != replying_user_id and photo['message_id'] not in seen_photos[replying_user_id]
    ]

    if unseen_photos:
        next_photo = random.choice(unseen_photos)
        new_message = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=next_photo['file_id'],
            caption="Reply to this photo to leave feedback and earn more points!"
        )
        context.bot_data.setdefault('photo_links', {})[new_message.message_id] = next_photo['user_id']
        context.bot_data.setdefault('photo_files', {})[new_message.message_id] = next_photo['file_id']
        seen_photos.setdefault(replying_user_id, set()).add(new_message.message_id)
    else:
        await update.message.reply_text("📭 You've rated all available photos. Check back later!")

    # Prevent replies to polls
    if update.message.reply_to_message.poll:
        await update.message.reply_text("💬 You can't comment on polls, only vote.")
        return






#feed function
async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    seen_ids = seen_photos.get(user_id, set())
    photo_links = context.bot_data.setdefault('photo_links', {})
    photo_files = context.bot_data.setdefault('photo_files', {})

    if not submitted_photos and not poll_groups:
        await update.message.reply_text("No photos have been submitted yet.")
        return

    # 👉 Add this right after the check
    await update.message.reply_text(
        "🪙 You get +1 point for voting in a poll and +2 points for leaving a short comment.\n"
        "🧠 Say what is already good and what could be improved.\n"
        "👁️ If you see the same photo again – just respond 'Seen'."
    )

    # Only show photos not submitted by the user and not seen before (by file_id)
    unseen_photos = []

    seen_file_ids = seen_photos.get(user_id, set())

    for photo in submitted_photos:
        if photo['user_id'] == user_id:
            continue  # Don’t show user their own photo

        if photo['file_id'] not in seen_file_ids:
            continue  # already seen

        # Limit: skip if exposure used up
        uploader_points = user_points.get(photo['user_id'], 0)
        if photo.get('comments', 0) >= uploader_points:
            continue  # exposure limit reached

        unseen_photos.append(photo)

    unseen_polls = []
    for poll in poll_groups:
        if poll['user_id'] == user_id:
            continue  # skip own poll

        if poll.get('poll_message_id') in seen_photos.get(user_id, set()):
            continue

        uploader_points = user_points.get(poll['user_id'], 0)
        if poll.get('vote_count', 0) >= uploader_points:
            continue  # limit reached

        unseen_polls.append(poll)

    if not unseen_photos and not unseen_polls:
        await update.message.reply_text("📭 You've seen all available photos. Check back later!")
        return

    if unseen_photos and (not unseen_polls or random.choice([True, False])):
        # Show a regular photo
        photo = random.choice(unseen_photos)

        sent_message = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo['file_id'],
            caption="Reply to this photo to leave feedback and earn points!"
        )

        seen_photos.setdefault(user_id, set()).add(photo['file_id'])
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

        # Step 3: mark as seen
        seen_photos.setdefault(user_id, set()).add(poll['poll_message_id'])

        return  # 🚨 prevent rest of the function from trying to access sent_message (photo)

    # Save mapping of this new message
    photo_links[sent_message.message_id] = photo['user_id']
    photo_files[sent_message.message_id] = photo['file_id']

    seen_photos.setdefault(user_id, set()).add(sent_message.message_id)









#points
async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    points = user_points.get(user_id, 0)
    await update.message.reply_text(f"🏆 You have {points} point(s).")

#poll command
async def pollme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    points = user_points.get(user_id, 0)

    if points < 1:
        await update.message.reply_text(
            "❌ You have 0 points.\n"
            "To earn points, use /feed and interact with others:\n"
            "• +1 point for voting\n"
            "• +2 points for commenting"
        )
        return

    poll_buffers[user_id] = []
    waiting_for_poll_photos.add(user_id)
    await update.message.reply_text(
        "📸 Please send up to 10 photos you'd like to include in the poll.\n"
        "When you're done, send /donepoll."
    )







#donepoll
async def donepoll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_points.get(user_id, 0) == 0:
        await update.message.reply_text(
            "❌ You have 0 points and cannot create a poll yet.\n"
            "Use /feed to vote or comment on others' photos to earn points:\n"
            "• +1 for voting\n"
            "• +2 for commenting"
        )
        return

    if user_id not in poll_buffers or not poll_buffers[user_id]:
        await update.message.reply_text("❌ You haven't submitted any photos yet.")
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
        'notified_count': 0,
        'vote_count': 0
    })


    # Step 1: Send album of photos
    media_group = [InputMediaPhoto(photo_id) for photo_id in photo_ids]
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)

    # Step 2: Prepare poll options
    options = [f"Photo {i+1}" for i in range(len(photo_ids))]

    # Step 3: Send anonymous poll
    poll_message = await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question="🗳️ Which photo(s) do you like the most best?",
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True
    )

    poll_groups[-1]['poll_id'] = poll_message.poll.id
    poll_groups[-1]['poll_message_id'] = poll_message.message_id

    user_points[user_id] = user_points.get(user_id, 0) - 1
    await update.message.reply_text(
        "✅ Your poll has been created and sent to voters!"
    )

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

    # 🧠 Step 4: Voter selection logic (first draft)
    owner_points = user_points.get(user_id, 1)
    available_voters = list(all_users - {user_id})

    if not available_voters:
        await update.message.reply_text("⚠️ No one else is using the bot yet to vote.")
        return

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
        await context.bot.send_message(voter_id, "🗳️ Please vote in the poll! You have 1 minute.")
    except:
        # If the user has blocked the bot or it can't message them
        await context.bot.send_message(owner_id, f"⚠️ Could not send poll to user {voter_id}.")






async def feed_from_poll_vote(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """After a user votes in a poll, show them the next photo or poll from feed."""
    try:
        chat = await context.bot.get_chat(user_id)

        dummy_update = Update(update_id=0, message=None)

        class DummyMessage:
            def __init__(self, user_id, chat_id):
                self.from_user = type("User", (), {"id": user_id})
                self.chat = type("Chat", (), {"id": chat_id})
                self.chat_id = chat_id
                self.message_id = 0

        dummy_update.effective_user = type("User", (), {"id": user_id})
        dummy_update.effective_chat = type("Chat", (), {"id": chat.id})
        dummy_update.message = DummyMessage(user_id, chat.id)

        await feed(dummy_update, context)

    except Exception as e:
        print(f"❌ Failed to trigger /feed after poll vote: {e}")






# launch the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('submit', submit))
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_reply))
    app.add_handler(CommandHandler('feed', feed))
    app.add_handler(CommandHandler('points', points))
    app.add_handler(CommandHandler('pollme', pollme))
    app.add_handler(CommandHandler('donepoll', donepoll))
    print("Bot is running...")
    app.run_polling()
