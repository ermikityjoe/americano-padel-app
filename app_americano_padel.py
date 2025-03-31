import math
import random
from itertools import combinations
import os # Para limpiar la consola (opcional)

def clear_console():
    """Limpia la consola para mejorar la legibilidad."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_tournament_config():
    """Recopila la configuración inicial del torneo."""
    print("--- CONFIGURACIÓN DEL TORNEO ---")
    name = input("Nombre del Torneo: ")
    while True:
        try:
            num_players = int(input("Número total de jugadores (debe ser par >= 4): "))
            if num_players >= 4 and num_players % 2 == 0:
                break
            else:
                print("Error: El número de jugadores debe ser par y al menos 4.")
        except ValueError:
            print("Error: Introduce un número válido.")

    while True:
        try:
            num_courts = int(input("Número de pistas disponibles (>= 1): "))
            if num_courts >= 1:
                break
            else:
                print("Error: Debe haber al menos 1 pista.")
        except ValueError:
            print("Error: Introduce un número válido.")

    print("\n--- REGISTRO DE JUGADORES ---")
    players = []
    for i in range(num_players):
        while True:
            player_name = input(f"Nombre del Jugador {i + 1}/{num_players}: ").strip()
            if player_name and player_name not in players:
                players.append(player_name)
                break
            elif not player_name:
                 print("Error: El nombre no puede estar vacío.")
            else:
                 print(f"Error: El jugador '{player_name}' ya está registrado.")
    
    return {
        "name": name,
        "num_players": num_players,
        "num_courts": num_courts,
        "players": players
    }

def generate_simplified_fixture(players, num_courts):
    """
    Genera un fixture simplificado para un torneo Americano.
    NOTA: Este es un algoritmo SIMPLIFICADO. No garantiza una rotación perfecta
    ni evita completamente la repetición de parejas en torneos largos.
    Se centra en crear rondas con partidos según las pistas disponibles.
    """
    num_players = len(players)
    # Un torneo americano completo suele tener N-1 rondas si N es el número de jugadores
    num_rounds = num_players - 1 
    
    fixture = {"rounds": []}
    
    # Copia para manipular sin alterar la original en cada ronda
    available_players = list(players) 
    
    # Historial simple para intentar variar parejas (muy básico)
    pairs_history = set() 

    for round_num in range(1, num_rounds + 1):
        round_matches = []
        # Barajar jugadores para intentar variar los enfrentamientos/parejas
        random.shuffle(available_players) 
        
        players_in_round = list(available_players) # Jugadores disponibles para esta ronda
        players_assigned_this_round = set()
        
        # Determinar cuántos partidos jugar (limitado por pistas o jugadores)
        max_matches_possible = len(players_in_round) // 4
        num_matches_this_round = min(max_matches_possible, num_courts)

        match_count = 0
        
        # Intentar formar partidos
        possible_pairs = list(combinations(players_in_round, 2))
        random.shuffle(possible_pairs) # Añadir aleatoriedad a la selección de parejas
        
        used_players_for_pairs = set()
        potential_matches_found = [] # (pair1, pair2)

        # 1. Formar parejas únicas para esta ronda
        round_pairs = []
        players_paired_this_round = set()
        for p1, p2 in possible_pairs:
             if p1 not in players_paired_this_round and p2 not in players_paired_this_round:
                 round_pairs.append(tuple(sorted((p1, p2))))
                 players_paired_this_round.add(p1)
                 players_paired_this_round.add(p2)

        # 2. Enfrentar parejas
        players_in_matches = set()
        possible_opponents = list(combinations(round_pairs, 2))
        random.shuffle(possible_opponents)

        for pair1, pair2 in possible_opponents:
             # Asegurarse de que los 4 jugadores son distintos
             players_in_potential_match = set(pair1) | set(pair2)
             if len(players_in_potential_match) == 4:
                 # Asegurarse de que ninguno de estos jugadores ya está en otro partido de esta ronda
                 if not any(p in players_in_matches for p in players_in_potential_match):
                     if match_count < num_matches_this_round:
                         potential_matches_found.append({
                             "court": match_count + 1,
                             "pair1": pair1,
                             "pair2": pair2,
                             "score1": None, # Placeholder para resultado
                             "score2": None  # Placeholder para resultado
                         })
                         players_in_matches.update(players_in_potential_match)
                         match_count += 1
                     else:
                         break # Suficientes partidos para las pistas disponibles

        round_matches = potential_matches_found
        players_resting = [p for p in players_in_round if p not in players_in_matches]

        fixture["rounds"].append({
            "round_num": round_num,
            "matches": round_matches,
            "resting": players_resting
        })

    return fixture

def display_round(round_data):
    """Muestra los partidos de una ronda específica."""
    print(f"\n--- RONDA {round_data['round_num']} ---")
    if not round_data['matches']:
        print("No hay partidos programados para esta ronda (posiblemente por nº jugadores/pistas).")
    else:
        for match in round_data['matches']:
            p1_name = f"{match['pair1'][0]} / {match['pair1'][1]}"
            p2_name = f"{match['pair2'][0]} / {match['pair2'][1]}"
            score_str = "Resultado pendiente"
            if match['score1'] is not None and match['score2'] is not None:
                score_str = f"{match['score1']} - {match['score2']}"
            
            print(f" Pista {match['court']}: {p1_name} vs {p2_name}  [{score_str}]")

    if round_data['resting']:
        print(f" Descansan: {', '.join(round_data['resting'])}")

def enter_results(fixture):
    """Permite al usuario introducir los resultados de los partidos."""
    print("\n--- ENTRADA DE RESULTADOS ---")
    num_rounds = len(fixture['rounds'])
    
    while True:
        try:
            round_choice = input(f"Introduce el número de ronda para ver/editar resultados (1-{num_rounds}, o 's' para salir): ")
            if round_choice.lower() == 's':
                break
            round_idx = int(round_choice) - 1
            if 0 <= round_idx < num_rounds:
                clear_console()
                selected_round = fixture['rounds'][round_idx]
                display_round(selected_round)
                
                if not selected_round['matches']:
                    input("No hay partidos en esta ronda. Pulsa Enter para continuar...")
                    clear_console()
                    continue

                match_choice = input(f"Introduce el número de pista para ingresar resultado (1-{len(selected_round['matches'])}), o 'v' para volver: ")
                if match_choice.lower() == 'v':
                    clear_console()
                    continue
                
                try:
                    match_idx = int(match_choice) -1 # Indice basado en pista, asumir correlativo
                    
                    # Buscar el match correspondiente a la pista (puede no ser igual al índice si las pistas no son 1, 2, 3...)
                    target_match = None
                    for m in selected_round['matches']:
                        if m['court'] == int(match_choice):
                             target_match = m
                             break
                    
                    if target_match and 0 <= match_idx < len(selected_round['matches']): # Doble check
                        p1_name = f"{target_match['pair1'][0]} / {target_match['pair1'][1]}"
                        p2_name = f"{target_match['pair2'][0]} / {target_match['pair2'][1]}"
                        
                        while True:
                            try:
                                score1_str = input(f"Games ganados por {p1_name}: ")
                                if score1_str.strip() == "": # Permitir borrar resultado
                                     score1 = None
                                else:
                                     score1 = int(score1_str)
                                     if score1 < 0: raise ValueError("Puntuación no puede ser negativa")
                                break
                            except ValueError:
                                print("Error: Introduce un número entero no negativo.")

                        while True:
                            try:
                                score2_str = input(f"Games ganados por {p2_name}: ")
                                if score2_str.strip() == "": # Permitir borrar resultado
                                     score2 = None
                                else:
                                     score2 = int(score2_str)
                                     if score2 < 0: raise ValueError("Puntuación no puede ser negativa")
                                break
                            except ValueError:
                                print("Error: Introduce un número entero no negativo.")

                        # Solo guardar si ambos son válidos o ambos son None
                        if (score1 is not None and score2 is not None) or \
                           (score1 is None and score2 is None):
                             target_match['score1'] = score1
                             target_match['score2'] = score2
                             print("Resultado guardado.")
                        else:
                             print("Error: Debes ingresar ambos scores o dejar ambos en blanco para borrar.")

                        input("Pulsa Enter para continuar...")
                        clear_console()
                    else:
                        print("Error: Número de pista inválido.")
                        input("Pulsa Enter para continuar...")
                        clear_console()

                except ValueError:
                    print("Error: Entrada inválida.")
                    input("Pulsa Enter para continuar...")
                    clear_console()

            else:
                print(f"Error: Ronda inválida. Debe ser entre 1 y {num_rounds}.")
                input("Pulsa Enter para continuar...")
                clear_console()

        except ValueError:
            print("Error: Introduce un número de ronda válido o 's'.")
            input("Pulsa Enter para continuar...")
            clear_console()
            
    clear_console()


def calculate_standings(players, fixture):
    """Calcula la clasificación basada en los resultados introducidos."""
    standings = {player: {"JG": 0, "JR": 0, "PG": 0, "PP": 0, "PE": 0, "PJ": 0} for player in players}

    for round_data in fixture['rounds']:
        for match in round_data['matches']:
            if match['score1'] is not None and match['score2'] is not None:
                s1 = match['score1']
                s2 = match['score2']
                pair1 = match['pair1']
                pair2 = match['pair2']

                # Actualizar Partidos Jugados
                for p in pair1: standings[p]['PJ'] += 1
                for p in pair2: standings[p]['PJ'] += 1

                # Actualizar Games Ganados/Recibidos
                for p in pair1:
                    standings[p]['JG'] += s1
                    standings[p]['JR'] += s2
                for p in pair2:
                    standings[p]['JG'] += s2
                    standings[p]['JR'] += s1

                # Actualizar Partidos Ganados/Perdidos/Empatados
                if s1 > s2:
                    for p in pair1: standings[p]['PG'] += 1
                    for p in pair2: standings[p]['PP'] += 1
                elif s2 > s1:
                    for p in pair1: standings[p]['PP'] += 1
                    for p in pair2: standings[p]['PG'] += 1
                else: # Empate
                    for p in pair1: standings[p]['PE'] += 1
                    for p in pair2: standings[p]['PE'] += 1

    # Calcular Diferencia de Games
    for player in standings:
        standings[player]['DG'] = standings[player]['JG'] - standings[player]['JR']
        
    # Ordenar: 1º DG (desc), 2º JG (desc)
    sorted_players = sorted(
        standings.keys(), 
        key=lambda p: (standings[p]['DG'], standings[p]['JG']), 
        reverse=True
    )

    return standings, sorted_players

def display_standings(standings, sorted_players, tournament_name):
    """Muestra la tabla de clasificación formateada."""
    print(f"\n--- CLASIFICACIÓN: {tournament_name} ---")
    print("-" * 70)
    print(f"{'Pos':<4} {'Jugador':<20} {'PJ':<4} {'PG':<4} {'PE':<4} {'PP':<4} {'JG':<5} {'JR':<5} {'DG':<5}")
    print("-" * 70)
    
    for i, player in enumerate(sorted_players):
        stats = standings[player]
        print(f"{i+1:<4} {player:<20} {stats['PJ']:<4} {stats['PG']:<4} {stats['PE']:<4} {stats['PP']:<4} {stats['JG']:<5} {stats['JR']:<5} {stats['DG']:<5}")
        
    print("-" * 70)

def export_standings_to_txt(standings, sorted_players, tournament_name):
    """Guarda la clasificación en un archivo de texto simple."""
    filename = f"clasificacion_{tournament_name.replace(' ', '_')}.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"--- CLASIFICACIÓN: {tournament_name} ---\n")
            f.write("-" * 70 + "\n")
            f.write(f"{'Pos':<4} {'Jugador':<20} {'PJ':<4} {'PG':<4} {'PE':<4} {'PP':<4} {'JG':<5} {'JR':<5} {'DG':<5}\n")
            f.write("-" * 70 + "\n")
            
            for i, player in enumerate(sorted_players):
                stats = standings[player]
                f.write(f"{i+1:<4} {player:<20} {stats['PJ']:<4} {stats['PG']:<4} {stats['PE']:<4} {stats['PP']:<4} {stats['JG']:<5} {stats['JR']:<5} {stats['DG']:<5}\n")
            
            f.write("-" * 70 + "\n")
        print(f"\nClasificación exportada a '{filename}'")
    except Exception as e:
        print(f"\nError al exportar a TXT: {e}")


# --- Flujo Principal de la Aplicación ---
if __name__ == "__main__":
    clear_console()
    config = get_tournament_config()
    clear_console()
    
    print(f"Generando fixture para '{config['name']}'...")
    # Usar una copia de la lista de jugadores para el fixture
    fixture_data = generate_simplified_fixture(list(config['players']), config['num_courts'])
    print("Fixture generado.")
    input("Pulsa Enter para continuar...")
    clear_console()

    while True:
        print(f"\n--- MENÚ PRINCIPAL: {config['name']} ---")
        print("1. Ver/Introducir Resultados por Ronda")
        print("2. Ver Clasificación Actual")
        print("3. Exportar Clasificación a TXT")
        print("4. Salir")
        
        choice = input("Selecciona una opción: ")
        
        if choice == '1':
            clear_console()
            enter_results(fixture_data)
        elif choice == '2':
            clear_console()
            standings, sorted_players = calculate_standings(config['players'], fixture_data)
            display_standings(standings, sorted_players, config['name'])
            input("\nPulsa Enter para volver al menú...")
            clear_console()
        elif choice == '3':
            clear_console()
            standings, sorted_players = calculate_standings(config['players'], fixture_data)
            display_standings(standings, sorted_players, config['name']) # Mostrar antes de exportar
            export_standings_to_txt(standings, sorted_players, config['name'])
            input("\nPulsa Enter para volver al menú...")
            clear_console()
        elif choice == '4':
            print("¡Hasta la próxima!")
            break
        else:
            print("Opción inválida. Inténtalo de nuevo.")
            input("Pulsa Enter para continuar...")
            clear_console()