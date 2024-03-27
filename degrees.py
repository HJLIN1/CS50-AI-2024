import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids (key是名字，value是id)
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people(主要整理people所有演過的電影)
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {   #用id作为key
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()  #set()是集合
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}  #如果這個名字不在names里，就加入；且names是以小寫名字為key, id為value
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies(整理movies的所有演員)
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"]) #把演員演過的電影加入people
                movies[row["movie_id"]]["stars"].add(row["person_id"])  #把電影的演員加入movies
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2: 
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"  #如果有輸入directory就用輸入的，沒有就用large?

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))  #讓使用者輸入名字
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)  #找出最短路徑(需自行實作的function!)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):   #印出每一步的資訊
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    start = Node(state=source, parent=None, action=None)  #建立起始節點
    frontier = QueueFrontier()  #建立frontier
    frontier.add(start)  #把起始節點加入frontier
    explored = set()  #建立explored集合

    #使用 BFS 搜索演員之間的最短路徑。BFS較適合用util.py裡的QueueFrontier，因為它是先進先出的，所以可以保證最短路徑的搜尋。
    #在搜索過程中，對於每個節點 (演員)，我們將其相鄰的節點（共同出演過同一電影的演員）加入前沿中，並記錄其父節點。
    #當我們找到目標演員時，通過回溯父節點來重構最短路徑。    
    while not frontier.empty():
        node = frontier.remove()
        if node.state == target:
            path = []
            while node.parent is not None:
                path.append((node.action, node.state))
                node = node.parent
            path.reverse()
            return path
        explored.add(node.state)
        for action, state in neighbors_for_person(node.state):
            #如果這個節點不在frontier裡，且不在explored裡，才能加入frontier。
            # 確保frontier沒有contains_state(state) 之目的 是為了避免重複加入同一個節點
            # 確保state不在explored裡 之目的 是為了避免走回頭路
            if not frontier.contains_state(state) and state not in explored:  
                child = Node(state=state, parent=node, action=action)
                frontier.add(child)
    return None

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:   #如果有多個人有同樣的名字，就要讓使用者選擇
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}") #印出所有同名的人的個資
        try:
            person_id = input("Intended Person ID: ") #讓使用者輸入id
            if person_id in person_ids:
                return person_id
        #比較try except的用法與if...raise Exception, else的用法，確保運行順序
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):  #找出與某人共同演過某部電影的人，並回傳(movie_id, person_id) pairs
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors  #回傳候選的(movie_id, person_id) pairs，以集合的形式


if __name__ == "__main__":
    main()