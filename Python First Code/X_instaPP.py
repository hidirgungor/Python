import instaloader
ig = instaloader.Instaloader()
profile = input(f"Kullanıcı adını yazınız: ")
ig.download_profile(profile, profile_pic_only = True)
