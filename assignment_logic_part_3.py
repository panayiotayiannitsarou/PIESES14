# 🔹 ΤΡΙΤΟ ΜΕΡΟΣ ΚΩΔΙΚΑ: Έλεγχοι & Τελική Κατανομή Μαθητών (Βήματα 5–8)

import random
from collections import defaultdict
import itertools

# ➤ Βήμα 5: Έλεγχος Ποιοτικών Χαρακτηριστικών Τοποθετημένων
# Ελέγχει ανά τμήμα: Φύλο, Καλή Γνώση Ελληνικών, Ικανοποιητική Μαθησιακή Ικανότητα
# Καταγράφει την κατανομή για καθοδήγηση επόμενων βημάτων (χωρίς μετακινήσεις)
def analyze_balance(df, num_classes):
    characteristics = ['ΦΥΛΟ', 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ', 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ']
    report = []

    for char in characteristics:
        counts = df.groupby('ΤΜΗΜΑ')[char].value_counts().unstack().fillna(0)
        report.append(f"\n📊 Κατανομή για χαρακτηριστικό: {char}")
        report.append(str(counts.astype(int)))
    return report

# ➤ Βήμα 6: Φιλικές Ομάδες ανά Γνώση Ελληνικών
# [παραμένει ίδιο όπως προηγουμένως]
# [...]

# ➤ Βήμα 7: Υπόλοιποι Μαθητές Χωρίς Φιλίες
# [παραμένει ίδιο όπως προηγουμένως]
# [...]

# ➤ Βήμα 8: Έλεγχος Ποιοτικών Χαρακτηριστικών & Διορθώσεις

def correct_imbalances(df, classes, locks):
    changed = False
    characteristics = ['ΦΥΛΟ', 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ', 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ']
    num_classes = len(classes)
    warnings = []

    for char in characteristics:
        counts = df.groupby('ΤΜΗΜΑ')[char].value_counts().unstack().fillna(0)
        if counts.shape[0] < 2:
            continue

        for val in counts.columns:
            vals = counts[val].tolist()
            max_v, min_v = max(vals), min(vals)
            if max_v - min_v > 3:
                # Προσπάθεια swap
                for t1, t2 in itertools.combinations(range(num_classes), 2):
                    cls1 = [s for s in classes[t1] if not locks[s] and df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == s, char].values[0] == val]
                    cls2 = [s for s in classes[t2] if not locks[s] and df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == s, char].values[0] != val]
                    for s1 in cls1:
                        for s2 in cls2:
                            if df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == s1, 'ΦΥΛΟ'].values[0] == df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == s2, 'ΦΥΛΟ'].values[0]:
                                classes[t1].remove(s1)
                                classes[t2].remove(s2)
                                classes[t1].append(s2)
                                classes[t2].append(s1)
                                df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == s1, 'ΤΜΗΜΑ'] = f'Τμήμα {t2+1}'
                                df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == s2, 'ΤΜΗΜΑ'] = f'Τμήμα {t1+1}'
                                changed = True
                                break
                        if changed:
                            break
                    if changed:
                        break
        if not changed and max_v - min_v > 3:
            warnings.append(f"⚠️ Παραμένει απόκλιση >3 για χαρακτηριστικό '{char}'")
    return warnings

# ➤ Συνδυαστική Συνάρτηση για Βήματα 5–8

def finalize_assignment(df, classes, locks):
    num_classes = len(classes)

    # Βήμα 5
    balance_report = analyze_balance(df, num_classes)

    # Βήμα 6
    assign_friendly_groups_by_language(df, classes, locks)

    # Βήμα 7
    assign_remaining_students(df, classes, locks)

    # Βήμα 8
    correction_warnings = correct_imbalances(df, classes, locks)

    return balance_report + correction_warnings
