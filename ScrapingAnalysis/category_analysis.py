from . import plt

def merge_sets(set1,set2,count1,count2,percentage):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    jc = intersection/union
    if jc >= (percentage/100):
        merged_set = set1.union(set2)
        merged_count = count1+count2
        return merged_set,merged_count
    return None,None

def jaccard_similarity(sets_dict,percentage):

    merged_dict = {}
    used = set()
    sets = list(sets_dict.items())
    for i in range (len(sets)):
        if i in used:
            continue
        set1,count1 = sets[i]

        for j in range (i+1,len(sets)):
            if j in used:
                continue
            set2,count2 = sets[j]

            merged_set,merged_count = merge_sets(set1,set2,count1,count2,percentage)

            if merged_set is not None:
                used.add(i)
                used.add(j)
                merged_dict[frozenset(merged_set)] = merged_count
                break


        if i not in used:
            merged_dict[set1] = count1

    return merged_dict

def recurse_jaccard_similarity(similarity_list,percentage):
    while True:
        latest_similarity = jaccard_similarity(similarity_list,percentage)

        if latest_similarity == similarity_list:
            break
        similarity_list = latest_similarity
    return similarity_list

def community_analysis(items:dict,percentage=100):
    sets = []

    communities = {}
    for item in items.values():

        community = set()

        for category in item['Category']:
            community.add(category[0])

        if len(community) >= 2:
            print(community)
            print(communities)
            print(frozenset(community) in communities)
            if frozenset(community) not in communities:
                communities[frozenset(community)] = 1
                print(community," : ",communities[frozenset(community)])
            elif frozenset(community) in communities:
                communities[frozenset(community)] += 1
                print(community," : ",communities[frozenset(community)])

    print('Before applying Jaccard similarity: ')
    for community,counter in communities.items():
        print(community," : ",counter)
        sets.append(community)
    if percentage != 100:
        print(f'After applying {percentage}% Jaccard similarity: ')
        communities = recurse_jaccard_similarity(communities,percentage)
    sets = []
    for community,counter in communities.items():
        print(community, " : ", counter)
        sets.append(community)

    sets = []

    for community in communities.keys():
        str_version = ""
        for category in community:
            str_version += f" {category} |"
        sets.append(str_version)

    counters = list(communities.values())
    fig = plt.figure(figsize=(10, 10))
    plt.barh(sets, counters, color='lightblue')
    plt.xlabel('Number')
    plt.ylabel('Community')
    plt.title('Bar chart for communities and their numbers.')
    plt.tight_layout(pad=3.0)
    return fig



