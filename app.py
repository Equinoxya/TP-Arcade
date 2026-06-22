import inquirer
from database import engine, Borne, Games_types
from sqlalchemy.orm import sessionmaker
from database import Status

Session = sessionmaker(bind = engine)
session = Session()

def menu():
    manager = ArcadeManager(session)
    while True:
        menu = [
            inquirer.List('Menu', 
                        message='Que voulez vous faire ?', 
                        choices=["Ajouter une borne", "Afficher toutes les bornes","Afficher toutes les bornes disponibles", "Lancer une partie", "Terminer une partie", "Mettre une borne en maintenance", "Afficher les statistiques", "Quitter"])
        ]
        result = inquirer.prompt(menu)
        choice = result['Menu']
        if choice == "Ajouter une borne":
            manager.add_borne()
        if choice == "Afficher toutes les bornes":
            manager.display_all()
        if choice == "Afficher toutes les bornes disponibles":
            manager.display_dispo()
        if choice == "Lancer une partie":
            manager.start_game()
        if choice == "Terminer une partie":
            manager.end_game()
        if choice == "Mettre une borne en maintenance":
            manager.maintenance()
        if choice == 'Afficher les statistiques':
            manager.statistics()
        if choice == 'Quitter':
            exit()

def main():
    menu()

class ArcadeManager:
    def __init__(self, session):
        self.session = session
    def add_borne(self):
        games_types_list = self.session.query(Games_types).all()
        availability = self.session.query(Status).all()
        choices_types = [gt.name for gt in games_types_list]
        choices_available = [a.name for a in availability]
        questions = [
            inquirer.Text('nom', message='Quel est le nom de la borne ?' ),
            inquirer.List('type', message='Quel type de jeu ?', 
                            choices= choices_types),
            inquirer.Text('prix', message='Quel est le prix d\'une partie ?'),
            inquirer.List('status', message= 'Quel est son statut ?',
                        choices= choices_available),
        ]
        answers = inquirer.prompt(questions)
        status_obj = self.session.query(Status).filter_by(name = answers['status']).first()
        borne = Borne(
            name = answers['nom'],
            borne_type = answers['type'],
            price = float(answers['prix']),
            status_id = status_obj.id,
            nb_games = 0
        )
        self.session.add(borne)
        self.session.commit()
        print("Borne ajoutée")
    def display_all(self):
        bornes = self.session.query(Borne).all()
        print('========Toutes les bornes========')
        for borne in bornes:
            print(f'Nom : {borne.name} || {borne.borne_type} || {borne.price}€ par partie || Nombre de parties jouées: {borne.nb_games} \n')
    def display_dispo(self):
        result = (
            self.session.query(
                Borne.name,
                Borne.price,
                Status.name
            )
            .join(Status)
            .filter(Status.name == "Disponible")
            .all()
        )
        for name, price, statut in result:
            print(f'Nom : {name} || {price}€ par partie ||{statut} \n')
    def start_game(self):
        borne_dispo=( 
        self.session.query(Borne)
        .join(Status)
        .filter(Status.name == "Disponible")
        .all()
        )
        if not borne_dispo:
            print("Aucune borne disponible")
            return
        choices = [borne.name for borne in borne_dispo]
        question = [
            inquirer.List("borne", message= "Sur quelle borne lancer la partie ?", 
                            choices=choices)
        ]
        answer = inquirer.prompt(question)
        borne = (
            self.session.query(Borne)
            .filter_by(name= answer["borne"])
            .first()
        )
        status = (
            self.session.query(Status)
            .filter_by(name= "Occupée")
            .first()
        )
        borne.status_id = status.id
        borne.nb_games += 1
        self.session.commit()
        print(f'Partie lancée sur {borne.name}')
    def end_game(self):
        borne_dispo=( 
        self.session.query(Borne)
        .join(Status)
        .filter(Status.name == "Occupée")
        .all()
        )
        if not borne_dispo:
            print("Aucune borne est occupée")
            return
        choices = [borne.name for borne in borne_dispo]
        question = [
            inquirer.List("borne", message= "Sur quelle borne terminer la partie ?", 
                            choices=choices)
        ]
        answer = inquirer.prompt(question)
        borne = (
            self.session.query(Borne)
            .filter_by(name= answer["borne"])
            .first()
        )
        status = (
            self.session.query(Status)
            .filter_by(name= "Disponible")
            .first()
        )
        borne.status_id = status.id
        self.session.commit()
        print(f'Partie terminée sur {borne.name}')
    def maintenance(self):
        bornes=( 
        self.session.query(Borne)
        .join(Status)
        .all()
        )
        choices = [borne.name for borne in bornes]
        question = [
            inquirer.List("borne", message= "Quelle borne voulez vous mettre en maintenance ?", 
                            choices=choices)
        ]
        answer = inquirer.prompt(question)
        borne = (
            self.session.query(Borne)
            .filter_by(name= answer["borne"])
            .first()
        )
        status = (
            self.session.query(Status)
            .filter_by(name= "Maintenance")
            .first()
        )
        borne.status_id = status.id
        self.session.commit()
        print(f' {borne.name} en maintenance')
    def statistics(self):

        total_bornes = self.session.query(Borne).count()

        dispo = (
            self.session.query(Borne)
            .join(Status)
            .filter(Status.name == "Disponible")
            .count()
        )

        occupees = (
            self.session.query(Borne)
            .join(Status)
            .filter(Status.name == "Occupée")
            .count()
        )

        maintenance = (
            self.session.query(Borne)
            .join(Status)
            .filter(Status.name == "Maintenance")
            .count()
        )

        total_games = sum(
            borne.nb_games
            for borne in self.session.query(Borne).all()
        )

        borne_populaire = (
            self.session.query(Borne)
            .order_by(Borne.nb_games.desc())
            .first()
        )

        print("\n===== STATISTIQUES =====")
        print(f"Nombre total de bornes : {total_bornes}")
        print(f"Bornes disponibles : {dispo}")
        print(f"Bornes occupées : {occupees}")
        print(f"Bornes en maintenance : {maintenance}")
        print(f"Nombre total de parties jouées : {total_games}")

        if borne_populaire:
            print(
                f"Borne la plus utilisée : "
                f"{borne_populaire.name} "
                f"({borne_populaire.nb_games} parties)"
            )

main()