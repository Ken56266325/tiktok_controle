#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import subprocess
import time
import schedule
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
import os

# Configuration
console = Console()
STATUS_FILE = "status.json"
GITHUB_REPO = "origin"
GITHUB_BRANCH = "main"

def print_banner():
    """Affiche une belle bannière de démarrage"""
    banner_text = """
██╗   ██╗███████╗██████╗ ██╗███████╗██╗ ██████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
██║   ██║██╔════╝██╔══██╗██║██╔════╝██║██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
██║   ██║█████╗  ██████╔╝██║█████╗  ██║██║     ███████║   ██║   ██║██║   ██║██╔██╗ ██║
╚██╗ ██╔╝██╔══╝  ██╔══██╗██║██╔══╝  ██║██║     ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
 ╚████╔╝ ███████╗██║  ██║██║██║     ██║╚██████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                        
         ███████╗██╗  ██╗██████╗ ██╗██████╗  █████╗ ████████╗██╗ ██████╗ ███╗   ██╗   
         ██╔════╝╚██╗██╔╝██╔══██╗██║██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║   
         █████╗   ╚███╔╝ ██████╔╝██║██████╔╝███████║   ██║   ██║██║   ██║██╔██╗ ██║   
         ██╔══╝   ██╔██╗ ██╔═══╝ ██║██╔══██╗██╔══██║   ██║   ██║██║   ██║██║╚██╗██║   
         ███████╗██╔╝ ██╗██║     ██║██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║   
         ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   
    """
    
    console.print(Panel.fit(
        banner_text,
        border_style="cyan",
        title="[bold yellow]🔒 SYSTÈME DE VÉRIFICATION DES ABONNEMENTS 🔒[/bold yellow]",
        subtitle="[italic green]Protection contre la fraude automatisée[/italic green]"
    ))

def log_message(message, level="info"):
    """Affiche un message avec horodatage"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if level == "info":
        console.print(f"[cyan][{timestamp}][/cyan] [blue]ℹ️  {message}[/blue]")
    elif level == "success":
        console.print(f"[cyan][{timestamp}][/cyan] [green]✅ {message}[/green]")
    elif level == "warning":
        console.print(f"[cyan][{timestamp}][/cyan] [yellow]⚠️  {message}[/yellow]")
    elif level == "error":
        console.print(f"[cyan][{timestamp}][/cyan] [red]❌ {message}[/red]")

def pull_from_github():
    """Récupère la dernière version depuis GitHub (seulement status6.json)"""
    try:
        log_message("Synchronisation avec GitHub...", "info")
        
        # Sauvegarder les modifications locales importantes
        subprocess.run(['git', 'stash', 'push', '-m', 'Auto-stash before pull'], 
                      capture_output=True, text=True)
        
        # Pull seulement les changements
        result = subprocess.run(['git', 'pull', GITHUB_REPO, GITHUB_BRANCH], 
                              capture_output=True, text=True, check=True)
        
        # Restaurer les modifications locales
        subprocess.run(['git', 'stash', 'pop'], 
                      capture_output=True, text=True)
        
        log_message("Synchronisation GitHub réussie", "success")
        return True
    except subprocess.CalledProcessError as e:
        log_message(f"Erreur lors de la synchronisation GitHub: {e.stderr if hasattr(e, 'stderr') else e}", "warning")
        log_message("Continuation sans synchronisation (mode local)", "info")
        return True  # Continuer même en cas d'erreur de sync

def push_to_github(message="Mise à jour automatique - désactivation des comptes expirés"):
    """Pousse les modifications vers GitHub (seulement status6.json)"""
    try:
        # Ajouter seulement le fichier status6.json comme fait le bot original
        subprocess.run(['git', 'add', STATUS_FILE], check=True)
        
        # Vérifier s'il y a des changements à committer
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        
        if STATUS_FILE in result.stdout:
            subprocess.run(['git', 'commit', '-m', message], check=True)
            subprocess.run(['git', 'push', GITHUB_REPO, GITHUB_BRANCH], check=True)
            log_message("Modifications poussées vers GitHub", "success")
        else:
            log_message("Aucune modification de status.json à pousser", "info")
        
        return True
    except subprocess.CalledProcessError as e:
        log_message(f"Erreur lors du push vers GitHub: {e}", "error")
        return False

def load_status():
    """Charge le fichier status6.json"""
    try:
        if not os.path.exists(STATUS_FILE):
            log_message(f"Fichier {STATUS_FILE} introuvable", "error")
            return None
            
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        log_message(f"Fichier {STATUS_FILE} chargé avec succès", "info")
        return data
    except Exception as e:
        log_message(f"Erreur lors du chargement du fichier: {e}", "error")
        return None

def save_status(data):
    """Sauvegarde le fichier status6.json"""
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log_message(f"Fichier {STATUS_FILE} sauvegardé", "success")
        return True
    except Exception as e:
        log_message(f"Erreur lors de la sauvegarde: {e}", "error")
        return False

def check_and_deactivate_expired():
    """Vérifie et désactive les comptes expirés"""
    log_message("🔍 Début de la vérification des abonnements...", "info")
    
    # Synchroniser avec GitHub (optionnel, continue même en cas d'erreur)
    pull_from_github()
    
    # Charger les données
    status_data = load_status()
    if not status_data or 'scripts' not in status_data:
        log_message("Impossible de charger les données, arrêt du processus", "error")
        return
    
    current_time = datetime.now()
    expired_users = []
    active_users = []
    
    # Créer un tableau pour l'affichage
    table = Table(title="📊 État des Abonnements", box=box.ROUNDED)
    table.add_column("ID Utilisateur", style="cyan", no_wrap=True)
    table.add_column("Plan", style="yellow")
    table.add_column("Date d'expiration", style="blue")
    table.add_column("Temps restant", style="green")
    table.add_column("Statut", style="bold")
    
    for user in status_data['scripts']:
        user_id = user.get('id', 'ID_INCONNU')
        plan = user.get('plan', 'INCONNU')
        countdown_time_str = user.get('countdown_start_time', '')
        
        if not countdown_time_str:
            continue
            
        try:
            # Parser la date d'expiration
            expiration_time = datetime.fromisoformat(countdown_time_str.replace('Z', '+00:00'))
            if expiration_time.tzinfo is not None:
                expiration_time = expiration_time.replace(tzinfo=None)
            
            # Calculer le temps restant
            time_remaining = expiration_time - current_time
            days_remaining = time_remaining.days
            
            # Formater l'affichage du temps restant
            if days_remaining < 0:
                time_str = f"{abs(days_remaining)}j [red]EXPIRÉ[/red]"
                status_str = "[red]❌ INACTIF[/red]"
                
                # Ajouter le statut inactif s'il n'existe pas
                if user.get('status') != 'inactive':
                    user['status'] = 'inactive'
                    expired_users.append({
                        'id': user_id,
                        'plan': plan,
                        'expired_since': abs(days_remaining)
                    })
            else:
                hours_remaining = time_remaining.seconds // 3600
                if days_remaining == 0:
                    time_str = f"{hours_remaining}h"
                else:
                    time_str = f"{days_remaining}j {hours_remaining}h"
                
                status_str = "[green]✅ ACTIF[/green]"
                
                # S'assurer que le statut est actif
                if user.get('status') != 'active':
                    user['status'] = 'active'
                
                active_users.append({
                    'id': user_id,
                    'plan': plan,
                    'days_remaining': days_remaining
                })
            
            # Ajouter à la table
            table.add_row(
                user_id[:12] + "..." if len(user_id) > 15 else user_id,
                plan,
                expiration_time.strftime("%d/%m/%Y %H:%M"),
                time_str,
                status_str
            )
            
        except Exception as e:
            log_message(f"Erreur lors du traitement de l'utilisateur {user_id}: {e}", "error")
    
    # Afficher le tableau
    console.print(table)
    
    # Résumé des actions
    if expired_users:
        log_message(f"🔒 {len(expired_users)} compte(s) désactivé(s) pour expiration", "warning")
        
        # Afficher les détails des comptes désactivés
        expired_table = Table(title="🚫 Comptes Désactivés", box=box.SIMPLE_HEAD)
        expired_table.add_column("ID", style="red")
        expired_table.add_column("Plan", style="yellow")
        expired_table.add_column("Expiré depuis", style="red")
        
        for user in expired_users:
            expired_table.add_row(
                user['id'][:20] + "..." if len(user['id']) > 23 else user['id'],
                user['plan'],
                f"{user['expired_since']} jour(s)"
            )
        
        console.print(expired_table)
        
        # Sauvegarder et pousser vers GitHub
        if save_status(status_data):
            commit_message = f"Désactivation automatique de {len(expired_users)} compte(s) expiré(s)"
            push_to_github(commit_message)
    else:
        log_message("✅ Aucun compte expiré trouvé", "success")
    
    # Statistiques finales
    stats_panel = Panel.fit(
        f"[green]Comptes actifs: {len(active_users)}[/green]\n"
        f"[red]Comptes expirés: {len(expired_users)}[/red]\n"
        f"[blue]Total: {len(active_users) + len(expired_users)}[/blue]",
        title="📈 Statistiques",
        border_style="green"
    )
    console.print(stats_panel)
    
    log_message("🔍 Vérification terminée", "success")
    print("-" * 80)

def main():
    """Fonction principale"""
    print_banner()
    
    # Vérification initiale des dépendances
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        log_message("Git détecté et fonctionnel", "success")
    except:
        log_message("Git n'est pas installé ou accessible", "error")
        return
    
    # Vérifier que nous sommes dans un dépôt Git
    if not os.path.exists('.git'):
        log_message("Ce répertoire n'est pas un dépôt Git", "error")
        return
    
    log_message("🚀 Démarrage du système de vérification", "success")
    log_message("⏰ Vérifications programmées toutes les heures", "info")
    
    # Programmer la vérification toutes les heures
    schedule.every().hour.do(check_and_deactivate_expired)
    
    # Première vérification immédiate
    check_and_deactivate_expired()
    
    log_message("🔄 Système en fonctionnement - Appuyez sur Ctrl+C pour arrêter", "info")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes s'il y a des tâches à exécuter
    except KeyboardInterrupt:
        log_message("🛑 Arrêt du système demandé par l'utilisateur", "warning")
        console.print(Panel.fit(
            "[yellow]Système arrêté proprement[/yellow]",
            title="👋 Au revoir !",
            border_style="yellow"
        ))

if __name__ == "__main__":
    main()
