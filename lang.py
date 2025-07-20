# lang.py

CELEBRITY_PRICE = 20  # або будь-яке інше значення, яке ти використовуєш
MONOBANK_LINK = "https://send.monobank.ua/jar/mvaEKosuB"  # посилання на оплату

messages = {
    'start': {
        'en': "👋 {name}, you have 50 points.\n"
        "/submit – send a photo\n"
        "/pollme – create a poll\n"
        "/feed – view others\n"
        "/rules – how it works",

        'uk': "👋 {name}, у тебе 50 балів.\n"
        "/submit – надіслати фото\n"
        "/pollme – створити опитування\n"
        "/feed – переглянути інших\n"
        "/rules – як це працює"
    },
    'submit_prompt': {
        'en': "📸 Send a photo and (if you want) a caption.\n"
        "💰 It costs 15 points. People will comment anonymously.",
        'uk': "📸 Надішли фото і (якщо хочеш) підпис.\n"
        "💰 Це коштує 15 балів. Люди коментуватимуть анонімно."
    },
    'banned': {
        'en': "🚫 You are banned from using this bot.",
        'uk': "🚫 Тобі заборонено користуватись цим ботом."
    },
    'not_enough_points': {
        'en': (
            "❌ You have 0 points.\n"
            "To earn points, use /feed and interact with others:\n"
            "• +1 point for voting\n"
            "• +2 points for commenting"
        ),
        'uk': (
            "❌ У вас 0 балів.\n"
            "Щоб заробити бали, використовуйте /feed та взаємодійте з іншими:\n"
            "• +1 бал за голосування\n"
            "• +2 бали за коментування"
        )
    },
    'poll_vote_received': {
        'en': "✅ Received vote for poll ID: {poll_id}",
        'uk': "✅ Отримано голос в опитуванні з ID: {poll_id}"
    },
    'poll_point_earned': {
        'en': "✅ {user_id} voted in a poll and earned 1 point.",
        'uk': "✅ {user_id} проголосував/ла в опитуванні, заробивши 1 бал."
    },
    'matching_poll_found': {
        'en': "📊 Matching poll found, owner: {owner_id}",
        'uk': "📊 Знайдено відповідне опитування, власник: {owner_id}"
    },
    'poll_result_notice': {
        'en': "🔻 You received 3 votes on your poll. 1 point has been deducted.",
        'uk': "🔻 Ви отримали 3 голоси у своєму опитуванні. 1 бал було списано."
    },
    'poll_vote_notice': {
        'en': "📬 Someone just voted in your poll!",
        'uk': "📬 Хтось щойно проголосував у твоєму опитуванні!"
    },
    'poll_vote_count': {
        'en': "📬 Your poll has received {vote_count} votes!",
        'uk': "📬 Твоє опитування отримало {vote_count} голос(ів)!"
    },
    'voting_closed_no_points': {
        'en': "❌ You're out of points. Voting is now closed!",
        'uk': "❌ У тебе закінчились бали. Голосування завершено!"
    },
    'poll_vote_details': {
        'en': "📬 {voter_name} voted in your poll!\n✅ Voted for: {options}",
        'uk': "📬 {voter_name} проголосував у твоєму опитуванні!\n✅ Обрано: {options}"
    },
    'poll_notify_error': {
        'en': "❌ Could not notify poll owner: {error}",
        'uk': "❌ Не вдалося сповістити власника опитування: {error}"
    },
    'need_payment_confirmation': {
        'en': "❌ You must confirm your payment with /paid before uploading photos.",
        'uk': "❌ Спочатку підтверди оплату командою /paid, перш ніж завантажувати фото."
    },
    'photo_received_expert_review': {
        'en': "✅ Photo received! An expert is reviewing it... You'll get a response soon. 😉",
        'uk': "✅ Фото отримано! Експерт уже переглядає його... Незабаром він надішле тобі відповідь. 😉"
    },
    'photo_send_failed': {
        'en': "❌ Failed to send your photo. Please try again later.",
        'uk': "❌ Не вдалося надіслати фото. Спробуй ще раз пізніше."
    },
    'photo_forward_error_log': {
        'en': "Error forwarding celebrity photo: {error}",
        'uk': "Помилка під час пересилання фото для Celebrity Match: {error}"
    },
    'max_photos_uploaded': {
        'en': "❌ You already uploaded 10 photos. Send /donepoll to proceed.",
        'uk': "❌ Ти вже завантажив 10 фото. Надішли /donepoll, щоб продовжити."
    },
    'poll_photo_saved': {
        'en': "✅ Photo {num} saved for poll.",
        'uk': "✅ Фото {num} збережено для опитування."
    },
    'please_use_submit': {
        'en': "⚠️ Please use /submit before sending a photo.",
        'uk': "⚠️ Спочатку введи /submit перед тим, як надіслати фото."
    },
    'new_photos_feed_notify': {
        'en': "📢 There are now {photo_count} photos to rate in /feed!\nGo earn points by commenting!",
        'uk': "📢 У стрічці /feed зараз {photo_count} фото для оцінки!\nЗаробляй бали, коментуй!"
    },
    'notify_user_error_log': {
        'en': "Could not notify user {uid}: {error}",
        'uk': "Не вдалося сповістити користувача {uid}: {error}"
    },
    'photo_submitted': {
        'en': "✅ Your photo has been submitted! Look now at others on /feed while waiting for comments!",
        'uk': "✅ Твоє фото надіслано! Переглянь інших у /feed поки чекаєш відгук!"
    },
    'poll_question_saved': {
       'en': "✅ Question saved. Now send up to 10 photos in one message, then type /donepoll.",
       'uk': "✅ Питання збережено. Тепер надішли до 10 фото одним повідомленням, а потім введи /donepoll."
    },
    'reply_no_match': {
        'en': "❌ This reply doesn't match any submitted photo.",
        'uk': "❌ Ця відповідь не відповідає жодному надісланому фото."
    },
    'already_commented': {
        'en': "⚠️ You already commented on this photo. Type /feed again",
        'uk': "⚠️ Ви вже залишили коментар до цього фото. Введідть /feed ще раз"
    },
    'comment_own_photo': {
        'en': "🤔 You can’t comment on your own photo.",
        'uk': "🤔 Ти не можеш коментувати власне фото."
    },
    'comment_points_awarded': {
        'en': "💬 You earned 2 points for commenting! Total: {points}",
        'uk': "💬 Ви отримали 2 бали за коментар! Разом: {points}"
    },
    'photo_reply_notification': {
        'en': "💬 Someone replied to your photo:\n\"{comment}\"",
        'uk': "💬 Хтось відповів на твоє фото:\n\"{comment}\""
    },
    'notify_uploader_error_log': {
        'en': "❌ Could not notify uploader: {error}",
        'uk': "❌ Не вдалося повідомити автора фото: {error}"
    },
    'comment_notification': {
        'en': "🔻 You received 3 comments on your photo(s). 1 point has been deducted.",
        'uk': "🔻 Ви отримали 3 коментарі до свого(їх) фото. 1 бал було списано."
    },
    'feed_photo_caption': {
        'en': "Tag to reply or press /feed if seen or commented.",
        'uk': "Тегніть, щоб відповісти, або натисніть /feed, якщо вже бачили чи коментували."
    },
    'no_more_photos': {
        'en': "📭 You've rated all available photos. Check back later!",
        'uk': "📭 Ви оцінили всі доступні фото. Повертайтеся пізніше!"
    },
    'no_comment_on_poll': {
        'en': "💬 You can't comment on polls, only vote.",
        'uk': "💬 Ви не можете коментувати опитування, тільки голосувати."
    },
    'no_photos_submitted': {
        'en': "No photos have been submitted yet.",
        'uk': "Жодного фото ще не надіслано."
    },
    'feed_instructions': {
        'en': "🏷️ TAG the photo to answer or press /feed if seen.",
        'uk': "🏷️ ТЕГАЙ фото, щоб відповісти, або натисни /feed, якщо вже бачив."
    },
    'all_photos_seen': {
        'en': "📭 You've seen all available photos. Check back later!",
        'uk': "📭 Ти переглянув усі доступні фото. Завітай пізніше!"
    },
    'photo_feedback_prompt': {
        'en': "💬 Reply with feedback to earn 2 points or press /feed!",
        'uk': "💬 Відповідай з відгуком, щоб заробити 2 бали або натисни /feed!"
    },
    'poll_voted_press_feed': {
        'en': "🗳️ Press /feed to see next.",
        'uk': "🗳️ Натисни /feed, щоб побачити наступне."
    },
    'points': {
        'en': "🏆 You have {points} point(s).",
        'uk': "🏆 У вас {points} бал(ів)."
    },
    'poll_photo_instructions': {
        'en': "📝 Write a question for a poll.",
        'uk': "📝 Напиши запитання для опитування."
    },
    'not_enough_points_poll': {
        'en': "❌ You need at least 15 points to create a poll.\n"
              "Use /feed to vote or comment on others' photos to earn points:\n"
              "• +1 for voting\n"
              "• +2 for commenting",
        'uk': "❌ Вам потрібно щонайменше 15 балів, щоб створити опитування.\n"
              "Використовуйте /feed, щоб голосувати або коментувати фото інших, щоб заробити бали:\n"
              "• +1 за голосування\n"
              "• +2 за коментування"
    },
    'no_photos_submitted': {
        'en': "❌ You haven't submitted any photos yet.",
        'uk': "❌ Ви ще не надіслали жодного фото."
    },
    'poll_question': {
        'en': "🗳️ Which photo(s) do you like the most?",
        'uk': "🗳️ Яке/які фото вам найбільше подобається(ються)?"
    },
    'poll_sent': {
        'en': "✅ Poll sent – 15 points used. Check your /feed while waiting for votes.",
        'uk': "✅ Опитування надіслано – списано 15 балів. Перегляньте свій /feed, поки чекаєте на голоси."
    },
    'please_vote': {
        'en': "🗳️ Please vote in the poll!",
        'uk': "🗳️ Будь ласка, проголосуйте в опитуванні!"
    },
    'poll_send_fail': {
        'en': "⚠️ Could not send poll to user {voter_id}.",
        'uk': "⚠️ Не вдалося надіслати опитування користувачу {voter_id}."
    },
    'last_photo_deleted': {
        'en': "✅ Your last submitted photo has been deleted.",
        'uk': "✅ Ваше останнє надіслане фото було видалено."
    },
    'last_poll_deleted': {
        'en': "✅ Your last poll has been deleted.",
        'uk': "✅ Ваше останнє опитування було видалено."
    },
    'nothing_to_delete': {
        'en': "⚠️ You haven't uploaded any photo or poll yet.",
        'uk': "⚠️ Ви ще не завантажили жодного фото чи опитування."
    },
    'nothing_found_to_delete': {
        'en': "⚠️ You don't have any photos or polls to delete.",
        'uk': "⚠️ У вас немає фото чи опитувань для видалення."
    },
    'deleted_all': {
        'en': "🧹 Deleted {deleted_photos} photo(s) and {deleted_polls} poll(s) you've submitted.",
        'uk': "🧹 Видалено {deleted_photos} фото та {deleted_polls} опитувань, які ви надіслали."
    },
    'report_reply_required': {
        'en': "⚠️ Please reply to the photo you want to report using /report.",
        'uk': "⚠️ Будь ласка, тегніть фото, на яке ви хочете поскаржитися, використовуючи /report."
    },
    'report_received': {
        'en': "✅ Report received. Thank you for helping us keep things safe.",
        'uk': "✅ Скарга отримана. Дякуємо, що допомагаєте нам підтримувати порядок."
    },
    'report_forward_fail': {
        'en': "❌ Failed to forward report: {error}",
        'uk': "❌ Не вдалося переслати скаргу: {error}"
    },
    'report_failed': {
        'en': "❌ Failed to report. Please try again later.",
        'uk': "❌ Не вдалося надіслати скаргу. Спробуйте ще раз пізніше."
    },
    'payment_already_confirmed': {
        'en': "✅ Payment already confirmed.\n📸 Please send a single photo with a clearly visible face.",
        'uk': "✅ Оплата вже підтверджена.\n📸 Будь ласка, надішліть одне фото з чітко видимим обличчям."
    },
    'celebrity_intro': {
        'en': (
            "💫 Want to know what celebrity you look like? We will create a manual report on what you can improve in your appearance and what celebrities you match. (THE SERVICE IS STILL IN DEVELOPMENT)\n"
            f"💰 This service costs {CELEBRITY_PRICE}₴.\n"
            f"🔗 Please pay here: {MONOBANK_LINK}\n"
            "Then type /paid once you've paid."
        ),
        'uk': (
            "💫 Хочете дізнатися, на яку знаменитість ви схожі? Ми вручну створимо звіт про те, що можна покращити у вашій зовнішності та з якими зірками у вас метч. (СЕРВІС ЩЕ В РОЗРОБЦІ)\n"
            f"💰 Ця функція коштує {CELEBRITY_PRICE}₴.\n"
            f"🔗 Будь ласка, сплатіть тут: {MONOBANK_LINK}\n"
            "Після оплати введіть /paid."
        )
    },
    'celebrity_result': {
        'en': "🌟 Here's your Celebrity Match result:\n\"{result}\"",
        'uk': "🌟 Ось ваш результат Celebrity Match:\n\"{result}\""
    },
    'payment_already_confirmed': {
        'en': "✅ You've already confirmed your payment. Use /celebrity_match to begin.",
        'uk': "✅ Ви вже підтвердили свою оплату. Введіть /celebrity_match, щоб почати."
    },
    'paid_confirmed': {
        'en': "✅ Payment confirmed! Now send /celebrity_match to submit a photo.",
        'uk': "✅ Оплата підтверджена! Тепер введіть /celebrity_match, щоб надіслати фото."
    },
    'help_message': {
        'en': (
            "*ImproveMyLook Bot – Commands & Rules*\n\n"
            "/submit – send a photo\n"
            "/pollme → /donepoll – create a poll\n"
            "/feed – view others, vote, and comment\n\n"
            "You start with 50 points. Each submission costs 15 points. If others vote in your poll, it also deducts points. You earn +1 point for voting and +2 points for commenting.\n\n"
            "/points – check your balance\n"
            "`/delete_last` – delete your last post\n"
            "`/delete_all` – delete all your posts\n"
            "/report – report a post\n\n"
            "`/celebrity_match` → /paid – get a match for 20₴, then send your photo\n\n"
            "`/buy_points` – buy 500 points for 20₴"
        ),
        'uk': (
            "*ImproveMyLook Bot – Команди та Правила*\n\n"
            "/submit – надіслати фото\n"
            "/pollme → /donepoll – створити опитування\n"
            "/feed – переглянути інших, голосувати та коментувати\n\n"
            "Ви починаєте з 50 балів. Кожне надсилання коштує 15 балів. Якщо інші голосують у вашому опитуванні, це також списує бали. Ви заробляєте +1 бал за голосування та +2 за коментування.\n\n"
            "/points – перевірити свій баланс\n"
            "/`delete_last` – видалити останній пост\n"
            "/`delete_all` – видалити всі ваші пости\n"
            "/report – поскаржитися на пост\n\n"
            "/`celebrity_match` → /paid – отримати метч за 20₴, потім надішліть своє фото\n\n"
            "/`buy_points` – купити 500 балів за 20₴" 
        )
    },
    'buy_points': {
        'en': "💸 *Buy 500 Points for 20₴!*\n\n"
              "🔗 Pay here: https://send.monobank.ua/jar/mvaEKosuB\n"
              "📩 After payment, send your receipt and Telegram ID (you can check it here @userinfobot) directly to me: @SireXl\n"
              "🪙 I will manually add 500 points to your account.",
        'uk': "💸 *Купи 500 балів за 20₴!*\n\n"
              "🔗 Сплатіть тут: https://send.monobank.ua/jar/mvaEKosuB\n"
              "📩 Після оплати надішліть свій чек та Телеграм ID (можна перевірити тут @userinfobot) мені: @SireXl\n"
              "🪙 Я вручну додам 500 балів до вашого рахунку."
    }
    













    # ➕ Add more messages as needed
}

def tr(lang, key, **kwargs):
    return messages[key][lang].format(**kwargs)
