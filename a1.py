import json
import os
import subprocess
from datetime import datetime, timedelta

# Fonctions d'affichage de couleurs et d'emoji
def print_banner():
    os.system('clear')
    print("\033[1;36m=================================\033[0m")
    print("\033[1;33m  Script Control Manager\033[0m")
    print("\033[1;36m=================================\033[0m")
    print("\033[1;32m 1️⃣ Ajouter une nouvelle ID\033[0m")
    print("\033[1;32m 2️⃣ Gérer les IDs existants\033[0m")
    print("\033[1;34m 4️⃣ Voir les références\033[0m")
    print("\033[1;35m 5️⃣ Ajouter/Modifier une annonce\033[0m")
    print("\033[1;31m 3️⃣ Quitter\033[0m")
    print("\033[1;36m=================================\033[0m")

def print_submenu():
    print("\033[1;35m=================================\033[0m")
    print("\033[1;34m 1️⃣ Activer/Désactiver\033[0m")
    print("\033[1;33m 2️⃣ Retour\033[0m")
    print("\033[1;31m 3️⃣ Supprimer l'ID\033[0m")
    print("\033[1;36m 4️⃣ Ajouter/Modifier Android ID\033[0m")
    print("\033[1;35m=================================\033[0m")

def print_modify_android_id_options():
    print("\033[1;35m=================================\033[0m")
    print("\033[1;32m 1️⃣ Modifier l'Android ID\033[0m")
    print("\033[1;33m 2️⃣ Retour au menu précédent\033[0m")
    print("\033[1;35m=================================\033[0m")

# Charger les données du fichier status1.json
def load_status():
    with open('status.json', 'r') as f:
        return json.load(f)

# Sauvegarder les données dans status1.json
def save_status(data):
    with open('status.json', 'w') as f:
        json.dump(data, f, indent=4)
    push_to_github()  # Pousser les modifications sur GitHub

# Push vers GitHub
def push_to_github():
    try:
        subprocess.run(['git', 'add', 'status.json'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Mise à jour de status.json'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("\033[1;32mModifications poussées vers GitHub.\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31mErreur lors du push vers GitHub : {e}\033[0m")

# Calculer le temps restant réel (ce qui est actuellement sur GitHub)
def calculate_actual_remaining_time(script):
    countdown_end = datetime.fromisoformat(script['countdown_start_time'])
    remaining_time = countdown_end - datetime.now()
    
    if remaining_time.total_seconds() <= 0:
        return 0, 0, 0
    
    days, seconds = remaining_time.days, remaining_time.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return days, hours, minutes

# Calculer le temps en pause (sauvegardé)
def calculate_paused_time(script):
    if 'paused_remaining_time' in script:
        total_seconds = script['paused_remaining_time']
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        return days, hours, minutes
    return 0, 0, 0

# Voir les références (format corrigé avec solde d'affiliation)
def view_references():
    data = load_status()
    print("\033[1;34m=== Références ===\033[0m")
    any_references = False

    for script in data['scripts']:
        referred_to = script.get('referred_to', [])
        if referred_to:
            any_references = True
            print(f"\033[1;33m- L'ID qui a référé : {script['id']} | Solde d'affiliation: {script.get('affiliation_balance', 0)} Ar\033[0m")
            for ref_id in referred_to:
                # Trouver les détails de l'ID référée
                ref_script = next((s for s in data['scripts'] if s['id'] == ref_id), None)
                if ref_script:
                    # Afficher le temps actuel
                    days, hours, minutes = calculate_actual_remaining_time(ref_script)
                    
                    # Afficher aussi le temps en pause s'il existe
                    pause_info = ""
                    if ref_script.get('countdown_paused', False):
                        p_days, p_hours, p_minutes = calculate_paused_time(ref_script)
                        pause_info = f" | Temps en pause: {p_days}j {p_hours}h {p_minutes}m"
                    
                    print(f"  ↪ {ref_script['id']} | Statut: {ref_script['status']} | Temps actuel: {days}j {hours}h {minutes}m{pause_info}")

    if not any_references:
        print("\033[1;31mAucune ID n'a référé d'autres IDs.\033[0m")
    else:
        print("\033[1;34mOptions supplémentaires : \033[0m")
        print("\033[1;32m1️⃣ Modifier le solde d'affiliation d'une ID qui a référé\033[0m")
        print("\033[1;33m2️⃣ Retour\033[0m")
        sub_choice = int(input("\033[1;36mEntrez votre choix: \033[0m"))

        if sub_choice == 1:
            modify_affiliation_balance(data)

    print("\033[1;33mAppuyez sur Entrée pour revenir au menu principal...\033[0m")
    input()

# Modifier le solde d'affiliation d'une ID
def modify_affiliation_balance(data):
    print("\033[1;34mEntrez l'ID qui a référé (pseudo): \033[0m")
    referer_id = input("\033[1;36mID: \033[0m")

    referer_script = next((script for script in data['scripts'] if script['id'] == referer_id and script.get('referred_to')), None)
    if not referer_script:
        print("\033[1;31mCet ID n'a référé personne. Action invalide.\033[0m")
        return

    print(f"\033[1;33mSolde actuel d'affiliation de {referer_id}: {referer_script.get('affiliation_balance', 0)} Ar\033[0m")
    print("\033[1;34mEntrez le nouveau solde d'affiliation (en Ariary): \033[0m")
    new_balance = int(input("\033[1;36mSolde: \033[0m"))

    referer_script['affiliation_balance'] = new_balance
    save_status(data)
    print(f"\033[1;32mLe solde d'affiliation de {referer_id} a été modifié avec succès à {new_balance} Ar.\033[0m")

# Ajouter une nouvelle ID
def add_new_id():
    data = load_status()
    print("\033[1;34mEntrez une nouvelle ID : \033[0m")
    new_id = input("\033[1;36mID: \033[0m")

    # Vérifier si l'ID existe déjà
    if any(script['id'] == new_id for script in data['scripts']):
        print(f"\033[1;31mL'ID {new_id} existe déjà. Veuillez en saisir une autre.\033[0m")
        return

    print("\033[1;34mEntrez l'Android ID de cette ID (ID unique de l'appareil) : \033[0m")
    android_id = input("\033[1;36mAndroid ID: \033[0m")

    print("\033[1;34mEntrez l'ID qui a référé cette ID (laissez vide si aucune) : \033[0m")
    referred_by = input("\033[1;36mRéféré par: \033[0m")

    print("\033[1;34mChoisissez le statut de l'ID : \033[0m")
    print("\033[1;32m1️⃣ Active\033[0m")
    print("\033[1;31m2️⃣ Inactive\033[0m")
    status_choice = input("\033[1;36mVotre choix: \033[0m")

    status = "active" if status_choice == '1' else "inactive"

    countdown_duration = timedelta(days=7)
    countdown_start_time = datetime.now() + countdown_duration

    new_entry = {
        'id': new_id,
        'android_id': android_id,
        'referred_by': referred_by if referred_by else None,
        'referred_to': [],
        'status': status,
        'countdown_start_time': countdown_start_time.isoformat(),
        'affiliation_balance': 0,
        'countdown_paused': False
    }
    data['scripts'].append(new_entry)

    if referred_by:
        for script in data['scripts']:
            if script['id'] == referred_by:
                script.setdefault('referred_to', []).append(new_id)
                break

    save_status(data)
    print(f"\033[1;32mID {new_id} ajoutée avec succès.\033[0m")

# Ajouter ou modifier une annonce
def add_or_modify_announcement(data):
    if 'announcement' in data:
        print(f"\033[1;33mAnnonce existante : {data['announcement']}\033[0m")
        print("\033[1;34mVoulez-vous la modifier? (oui/non): \033[0m")
        modify_choice = input("\033[1;36mVotre choix: \033[0m")

        if modify_choice.lower() == 'oui':
            print("\033[1;34mEntrez la nouvelle annonce: \033[0m")
            announcement = input("\033[1;36mAnnonce: \033[0m")
            data['announcement'] = announcement
            save_status(data)
            print(f"\033[1;32mAnnonce modifiée avec succès.\033[0m")
        else:
            print("\033[1;31mAucune modification effectuée.\033[0m")
    else:
        print("\033[1;34mEntrez une annonce à ajouter: \033[0m")
        announcement = input("\033[1;36mAnnonce: \033[0m")
        data['announcement'] = announcement
        save_status(data)
        print(f"\033[1;32mAnnonce ajoutée avec succès.\033[0m")

# Afficher les informations détaillées d'une ID
def display_id_info(selected_script):
    print(f"\033[1;34m=== Informations de l'ID: {selected_script['id']} ===\033[0m")
    
    # Android ID
    android_id = selected_script.get('android_id', 'Non défini')
    print(f"\033[1;33mAndroid ID: {android_id}\033[0m")
    
    # Statut
    print(f"\033[1;33mStatut: {selected_script['status']}\033[0m")
    
    # Solde d'affiliation (seulement s'il y en a un)
    affiliation_balance = selected_script.get('affiliation_balance', 0)
    if affiliation_balance > 0:
        print(f"\033[1;33mSolde d'affiliation: {affiliation_balance} Ar\033[0m")
    
    # Temps actuel
    days, hours, minutes = calculate_actual_remaining_time(selected_script)
    print(f"\033[1;33mTemps actuel: {days}j {hours}h {minutes}m\033[0m")
    
    # Temps en pause (si existe)
    if selected_script.get('countdown_paused', False):
        p_days, p_hours, p_minutes = calculate_paused_time(selected_script)
        print(f"\033[1;33mTemps en pause: {p_days}j {p_hours}h {p_minutes}m\033[0m")
    
    # Plan
    plan = selected_script.get('plan', 'Null')
    if plan == 'Basique':
        plan_display = "🟢 Basique"
    elif plan == 'VIP':
        plan_display = "⭐ VIP"
    else:
        plan_display = "❓ Null"
    print(f"\033[1;33mPlan: {plan_display}\033[0m")
    
    print("\033[1;36m=================================\033[0m")

# Gérer les IDs existants
def manage_existing_ids():
    data = load_status()
    print("\033[1;34m=== Liste des IDs existantes ===\033[0m")
    
    # Afficher toutes les IDs avec leurs statuts
    for script in data['scripts']:
        # Calcul du temps actuel
        days, hours, minutes = calculate_actual_remaining_time(script)
        
        # Déterminer le plan avec emoji
        plan = script.get('plan', 'Null')
        if plan == 'Basique':
            plan_display = "🟢 Basique"
        elif plan == 'VIP':
            plan_display = "⭐ VIP"
        else:
            plan_display = "❓ Null"
        
        status_display = script['status']
        pause_info = ""
        if script.get('countdown_paused', False):
            p_days, p_hours, p_minutes = calculate_paused_time(script)
            pause_info = f" | Temps en pause: {p_days}j {p_hours}h {p_minutes}m"
        
        print(f"ID: {script['id']} | Statut: {status_display} | Temps actuel: {days}j {hours}h {minutes}m{pause_info} | Plan: {plan_display}")

    print("\033[1;36mEntrez l'ID à gérer (ou 'retour' pour revenir) : \033[0m")
    choice = input("\033[1;36mID: \033[0m").strip()

    if choice.lower() == 'retour':
        return

    # Rechercher l'ID dans la liste
    selected_script = next((script for script in data['scripts'] if script['id'] == choice), None)
    
    if not selected_script:
        print(f"\033[1;31mL'ID {choice} n'existe pas.\033[0m")
        return

    # Afficher les informations détaillées de l'ID
    display_id_info(selected_script)

    print("=================================")
    print(" 1️⃣ Activer/Désactiver")
    print(" 2️⃣ ⏸️ Pause/Play le Compte à Rebours")
    print(" 3️⃣ Supprimer l'ID")
    print(" 4️⃣ Ajouter/Modifier Android ID")
    print(" 5️⃣ Ajouter/Modifier un Plan")
    print(" 6️⃣ Modifier/Gérer le Compte à Rebours")
    print(" 0️⃣ Retour")
    print("=================================")
    sub_choice = int(input("\033[1;36mEntrez votre choix: \033[0m"))

    if sub_choice == 1:
        if selected_script['status'] == 'inactive':
            print(f"\033[1;34mL'ID {selected_script['id']} sera maintenant activée.\033[0m")
            selected_script['status'] = 'active'
            
            # Si l'ID était en pause, restaurer le temps restant
            if selected_script.get('countdown_paused', False) and 'paused_remaining_time' in selected_script:
                # Restaurer le temps à partir du temps en pause
                new_end_time = datetime.now() + timedelta(seconds=selected_script['paused_remaining_time'])
                selected_script['countdown_start_time'] = new_end_time.isoformat()
                selected_script['countdown_paused'] = False
                del selected_script['paused_remaining_time']
            else:
                # Nouveau compte à rebours de 7 jours
                selected_script['countdown_start_time'] = (datetime.now() + timedelta(days=7)).isoformat()
            
            save_status(data)
            print(f"\033[1;32mID {selected_script['id']} activée avec succès.\033[0m")
        else:
            print(f"\033[1;34mL'ID {selected_script['id']} sera maintenant désactivée.\033[0m")
            selected_script['status'] = 'inactive'
            
            # Si en pause, nettoyer les données de pause
            if selected_script.get('countdown_paused', False):
                selected_script['countdown_paused'] = False
                if 'paused_remaining_time' in selected_script:
                    del selected_script['paused_remaining_time']
            
            save_status(data)
            print(f"\033[1;32mID {selected_script['id']} désactivée avec succès.\033[0m")

    elif sub_choice == 2:
        # Pause/Play direct
        if selected_script.get('countdown_paused', False):
            # Reprendre le compte à rebours
            print(f"\033[1;34mLe compte à rebours de l'ID {selected_script['id']} sera maintenant repris.\033[0m")
            
            # Restaurer le temps restant
            if 'paused_remaining_time' in selected_script:
                new_end_time = datetime.now() + timedelta(seconds=selected_script['paused_remaining_time'])
                selected_script['countdown_start_time'] = new_end_time.isoformat()
                del selected_script['paused_remaining_time']
            
            selected_script['countdown_paused'] = False
            
            # Activer seulement si c'était inactive
            if selected_script['status'] == 'inactive':
                selected_script['status'] = 'active'
        else:
            # Mettre en pause
            print(f"\033[1;34mLe compte à rebours de l'ID {selected_script['id']} sera maintenant mis en pause.\033[0m")
            
            # Calculer et sauvegarder le temps restant
            countdown_end = datetime.fromisoformat(selected_script['countdown_start_time'])
            remaining_time = countdown_end - datetime.now()
            
            if remaining_time.total_seconds() > 0:
                selected_script['paused_remaining_time'] = int(remaining_time.total_seconds())
            else:
                selected_script['paused_remaining_time'] = 0
            
            # Mettre le compte à rebours actuel à 0
            selected_script['countdown_start_time'] = datetime.now().isoformat()
            
            selected_script['countdown_paused'] = True
        
        save_status(data)
        print(f"\033[1;32mLe compte à rebours de l'ID {selected_script['id']} a été mis à jour avec succès.\033[0m")

    elif sub_choice == 0:
        return
    elif sub_choice == 3:
        print(f"\033[1;31mSuppression de l'ID {selected_script['id']}...\033[0m")
        # Supprimer cette ID des listes referred_to des autres IDs
        for script in data['scripts']:
            if selected_script['id'] in script.get('referred_to', []):
                script['referred_to'].remove(selected_script['id'])
        data['scripts'].remove(selected_script)
        save_status(data)
        print(f"\033[1;32mL'ID {selected_script['id']} a été supprimée avec succès.\033[0m")
    elif sub_choice == 4:
        if 'android_id' in selected_script:
            print(f"\033[1;31mL'Android ID de {selected_script['id']} existe déjà: {selected_script['android_id']}\033[0m")
            print_modify_android_id_options()
            modify_choice = int(input("\033[1;36mEntrez votre choix: \033[0m"))

            if modify_choice == 1:
                print("\033[1;34mEntrez le nouvel Android ID : \033[0m")
                android_id = input("\033[1;36mAndroid ID: \033[0m")
                selected_script['android_id'] = android_id
                save_status(data)
                print(f"\033[1;32mL'Android ID de {selected_script['id']} a été modifié avec succès.\033[0m")
            elif modify_choice == 2:
                return
        else:
            print("\033[1;34mEntrez l'Android ID de cette ID: \033[0m")
            android_id = input("\033[1;36mAndroid ID: \033[0m")
            selected_script['android_id'] = android_id
            save_status(data)
            print(f"\033[1;32mL'Android ID de {selected_script['id']} a été ajouté avec succès.\033[0m")
    elif sub_choice == 5:
        print("\033[1;36mChoisissez un plan pour cette ID:\033[0m")
        print("1. 🟢 Plan Basique")
        print("2. ⭐ Plan VIP")
        plan_choice = int(input("\033[1;36mEntrez votre choix: \033[0m"))

        if plan_choice == 1:
            selected_script['plan'] = 'Basique'
            print(f"\033[1;32mPlan 🟢 Basique sélectionné pour l'ID {selected_script['id']}.\033[0m")
        elif plan_choice == 2:
            selected_script['plan'] = 'VIP'
            print(f"\033[1;32mPlan ⭐ VIP sélectionné pour l'ID {selected_script['id']}.\033[0m")
        else:
            print("\033[1;31mChoix de plan invalide. Aucun changement effectué.\033[0m")
        save_status(data)
        print("\033[1;36mRevenir au menu principal...\033[0m")
    
    elif sub_choice == 6:
        print("\033[1;36mChoisissez une option pour modifier le compte à rebours:\033[0m")
        print("1. ⏱️ Modifier le compte à rebours de l'ID choisie")
        print("2. ⏸️ Mettre en pause/Reprendre le compte à rebours de toutes les IDs existantes")
        print("3. 🔙 Retour au menu principal")
        countdown_choice = int(input("\033[1;36mEntrez votre choix: \033[0m"))

        if countdown_choice == 1:
            print("\033[1;34mEntrez le nouveau compte à rebours (Jours Heures Minutes): \033[0m")
            days = int(input("\033[1;36mJours: \033[0m"))
            hours = int(input("\033[1;36mHeures: \033[0m"))
            minutes = int(input("\033[1;36mMinutes: \033[0m"))
            new_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)
            selected_script['countdown_start_time'] = new_time.isoformat()
            
            # Désactiver la pause si elle était active
            if selected_script.get('countdown_paused', False):
                selected_script['countdown_paused'] = False
                if 'paused_remaining_time' in selected_script:
                    del selected_script['paused_remaining_time']
            
            save_status(data)
            print(f"\033[1;32mLe compte à rebours de l'ID {selected_script['id']} a été modifié avec succès.\033[0m")

        elif countdown_choice == 2:
            print("\033[1;36mMettre en pause/Reprendre tous les compteurs existants...\033[0m")
            
            for script in data['scripts']:
                if script.get('countdown_paused', False):
                    # Reprendre
                    if 'paused_remaining_time' in script:
                        new_end_time = datetime.now() + timedelta(seconds=script['paused_remaining_time'])
                        script['countdown_start_time'] = new_end_time.isoformat()
                        del script['paused_remaining_time']
                    script['countdown_paused'] = False
                    if script['status'] == 'inactive':
                        script['status'] = 'active'
                else:
                    # Mettre en pause
                    if script['status'] == 'active' or True:  # Mettre en pause même si inactive
                        countdown_end = datetime.fromisoformat(script['countdown_start_time'])
                        remaining_time = countdown_end - datetime.now()
                        
                        if remaining_time.total_seconds() > 0:
                            script['paused_remaining_time'] = int(remaining_time.total_seconds())
                        else:
                            script['paused_remaining_time'] = 0
                        
                        # Mettre le compte à rebours actuel à 0
                        script['countdown_start_time'] = datetime.now().isoformat()
                        script['countdown_paused'] = True
            
            save_status(data)
            print("\033[1;32mTous les compteurs ont été mis à jour.\033[0m")

        elif countdown_choice == 3:
            return

# Fonction principale du script
def main():
    while True:
        print_banner()
        choice = input("\033[1;36mVotre choix: \033[0m").strip()
        
        if choice == '1':
            add_new_id()
        elif choice == '2':
            manage_existing_ids()
        elif choice == '4':
            view_references()
        elif choice == '5':
            data = load_status()
            add_or_modify_announcement(data)
        elif choice == '3':
            print("\033[1;31mAu revoir!\033[0m")
            break
        else:
            print("\033[1;31mChoix invalide. Essayez de nouveau.\033[0m")

if __name__ == '__main__':
    main()