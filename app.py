
import streamlit as st
import pandas as pd
import math
from io import BytesIO

# ➤ Import Λογικής Κατανομής από άλλα αρχεία
from assignment_logic_part_2 import apply_assignment_logic, initialize_classes
from assignment_logic_part_3 import finalize_assignment

# ➤ Κλείδωμα πρόσβασης με κωδικό
st.sidebar.title("🔐 Κωδικός Πρόσβασης")
password = st.sidebar.text_input("Εισάγετε τον κωδικό:", type="password")
if password != "katanomi2025":
    st.warning("❌ Λάθος κωδικός. Η πρόσβαση δεν επιτρέπεται.")
    st.stop()

# ➤ Ενεργοποίηση/Απενεργοποίηση Εφαρμογής
enable_app = st.sidebar.checkbox("✅ Ενεργοποίηση Εφαρμογής", value=True)
if not enable_app:
    st.info("🔒 Η εφαρμογή είναι προσωρινά απενεργοποιημένη.")
    st.stop()

# ➤ Νομική Προστασία
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 Παναγιώτα Γιαννίτσαρου | Όλα τα δικαιώματα διατηρούνται.")
st.sidebar.markdown("Η χρήση της εφαρμογής επιτρέπεται μόνο με ρητή γραπτή άδεια της δημιουργού.")

# ➤ Υπολογισμός Αριθμού Τμημάτων
def υπολογισμος_τμηματων(df):
    return math.ceil(len(df) / 25)

# ➤ Streamlit interface
st.title("📊 Κατανομή Μαθητών Α' Δημοτικού")
uploaded_file = st.file_uploader("🔹 Εισαγωγή Excel αρχείου μαθητών", type=[".xls", ".xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Το αρχείο φορτώθηκε επιτυχώς.")
    st.dataframe(df.head())

    if st.button("🔹 Κατανομή Μαθητών"):
        num_classes = υπολογισμος_τμηματων(df)
        st.info(f"📌 Υπολογίστηκαν {num_classes} τμήματα για {len(df)} μαθητές.")

        # Βήματα 1–4
        df = apply_assignment_logic(df, num_classes)

        # Επαναφορά λιστών για Βήματα 5–8
        classes = initialize_classes(num_classes)
        locks = {name: True for name in df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == True]['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']}
        for _, row in df[df['ΤΜΗΜΑ'].notna()].iterrows():
            index = int(row['ΤΜΗΜΑ'].split()[-1]) - 1
            classes[index].append(row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'])

        # Βήματα 5–8
        warnings = finalize_assignment(df, classes, locks)

        st.success("✅ Ολοκληρώθηκε η κατανομή όλων των βημάτων (1–8).")
        if warnings:
  st.warning("🔎 Παρατηρήσεις:\n" + "\n".join(warnings))

" + "\n".join(warnings))
        st.dataframe(df)

    if st.button("🔹 Εξαγωγή Excel Αποτελέσματος"):
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        st.download_button("📥 Κατέβασε το αρχείο Excel", data=output, file_name="katanomi.xlsx")

    if st.button("📊 Προβολή Στατιστικών Στοιχείων"):
        if 'ΤΜΗΜΑ' not in df.columns:
            st.error("⚠️ Δεν υπάρχει στήλη 'ΤΜΗΜΑ' στο αρχείο.")
        else:
            stats = df.groupby('ΤΜΗΜΑ').agg({
                'ΦΥΛΟ': [
                    ('Αγόρια', lambda x: (x == 'Α').sum()),
                    ('Κορίτσια', lambda x: (x == 'Κ').sum())
                ],
                'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ': ('Παιδιά Εκπαιδευτικών', lambda x: (x == 'Ν').sum()),
                'ΖΩΗΡΟΣ': ('Ζωηροί', lambda x: (x == 'Ν').sum()),
                'ΙΔΙΑΙΤΕΡΟΤΗΤΑ': ('Ιδιαιτερότητα', lambda x: (x == 'Ν').sum()),
                'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ': ('Καλή Γν. Ελληνικών', lambda x: (x == 'Ν').sum()),
                'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ': ('Μαθησιακά Ικανοί', lambda x: (x == 'Ν').sum()),
                'ΟΝΟΜΑΤΕΠΩΝΥΜΟ': ('Σύνολο Μαθητών', 'count')
            })
            stats.columns = stats.columns.droplevel(0)
            total_row = stats.sum(numeric_only=True)
            total_row.name = 'Σύνολο'
            stats = pd.concat([stats, total_row.to_frame().T])
            st.dataframe(stats)

            output_stats = BytesIO()
            stats.to_excel(output_stats)
            output_stats.seek(0)
            st.download_button("📥 Κατέβασε Στατιστικά σε Excel", data=output_stats, file_name="statistika_tmimata.xlsx")
else:
    st.warning("📂 Παρακαλώ εισάγετε πρώτα ένα αρχείο Excel.")
