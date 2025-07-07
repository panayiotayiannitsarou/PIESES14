# 🔹 ΔΕΥΤΕΡΟ ΜΕΡΟΣ ΚΩΔΙΚΑ: Λογική Κατανομής Μαθητών

# ➤ Συνάρτηση για έλεγχο πλήρως αμοιβαίας φιλίας
def is_mutual_friend(df, child1, child2):
    f1 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child1, 'ΦΙΛΟΙ'].values[0]).replace(' ', '').split(',')
    f2 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child2, 'ΦΙΛΟΙ'].values[0]).replace(' ', '').split(',')
    return child2 in f1 and child1 in f2

# ➤ Συνάρτηση για αποφυγή σύγκρουσης
def has_conflict(df, child1, child2):
    conflicts = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child1, 'ΣΥΓΚΡΟΥΣΕΙΣ'].values[0]).replace(' ', '').split(',')
    return child2 in conflicts

# ➤ Αρχικοποίηση Λίστας Τμημάτων
def initialize_classes(num_classes):
    return [[] for _ in range(num_classes)]

# ➤ Ανάθεση μαθητή σε τμήμα
def assign_to_class(df, student_name, classes, locks, avoid_lively=False):
    sizes = [len(cls) for cls in classes]
    min_size = min(sizes)
    for i, cls in enumerate(classes):
        if len(cls) == min_size:
            if all(not has_conflict(df, student_name, other) for other in cls):
                if avoid_lively:
                    cls_df = df[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(cls)]
                    if (cls_df['ΖΩΗΡΟΣ'] == 'Ν').any():
                        continue
                cls.append(student_name)
                locks[student_name] = True
                df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == student_name, 'ΤΜΗΜΑ'] = f'Τμήμα {i+1}'
                return True
    return False

# ➤ Βήμα 4: Φίλοι Παιδιών Βημάτων 1–3

def assign_friends_of_assigned(df, classes, locks):
    assigned = df[df['ΤΜΗΜΑ'].notna()]['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].tolist()
    unassigned = df[(df['ΤΜΗΜΑ'].isna()) & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False)]
    used = set()

    for _, row in unassigned.iterrows():
        name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        if name in used:
            continue

        friends = str(row['ΦΙΛΟΙ']).replace(' ', '').split(',')

        for friend in friends:
            if (
                friend in assigned and
                is_mutual_friend(df, name, friend) and
                not has_conflict(df, name, friend)
            ):
                friend_class = df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == friend, 'ΤΜΗΜΑ'].values[0]
                class_index = int(friend_class.split()[-1]) - 1

                if len(classes[class_index]) < 25:
                    classes[class_index].append(name)
                    df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name, 'ΤΜΗΜΑ'] = friend_class
                    locks[name] = True
                    used.add(name)
                break

    # Κλείδωμα όλων όσων έχουν πλέον τοποθετηθεί
    for name in df[df['ΤΜΗΜΑ'].notna()]['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']:
        locks[name] = True
    df['ΚΛΕΙΔΩΜΕΝΟΣ'] = df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(locks)


# ➤ Εφαρμογή Όλων των Βημάτων 1–4

def apply_assignment_logic(df, num_classes):
    classes = initialize_classes(num_classes)
    locks = {name: False for name in df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']}

    # Βήμα 1
    assign_teacher_children(df, classes, locks)

    # Βήμα 2
    assign_lively_students(df, classes, locks)

    # Βήμα 3
    assign_special_needs(df, classes, locks)

    # Βήμα 4
    assign_friends_of_assigned(df, classes, locks)

    return df
