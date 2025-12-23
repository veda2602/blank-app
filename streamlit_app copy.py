import streamlit as st
import pandas as pd
import numpy as np

# ================= PAGE CONFIG =================
st.set_page_config(page_title="NLA Parser", layout="wide")
st.title("Program Olah Data NLA by Veda 😂😍🙏")

# ================= UPLOAD FILE =================
uploaded_files = st.file_uploader(
    "Silakan Upload Filenya 🙏 (.xls)",
    type=["xls", "txt"],
    accept_multiple_files=True
)

# ================= FUNCTION =================
def process_file(uploaded_file):
    # ---------- READ FILE ----------
    data = pd.read_csv(uploaded_file, sep="\t", header=0)
    data = data.rename(columns={data.columns[0]: "raw"})

    # ---------- CLEAN XML ----------
    clean = (
        data["raw"]
        .astype(str)
        .str.replace(r"<.*?>", "", regex=True)
        .str.replace("&nbsp;", "", regex=True)
        .str.strip()
    )

    clean = clean.replace(r"^\s*$", np.nan, regex=True)
    clean = clean.dropna().reset_index(drop=True)

    # ---------- PARSING ----------
    rows = []
    current = {
        "P/N": None,
        "S/N": None,
        "P/N Description": None,
        "Batch": None
    }

    pn_assy = None
    sn_assy = None

    i = 0
    while i < len(clean):
        value = clean[i]

        if value == "P/N":
            if any(current.values()):
                rows.append(current)
                current = {
                    "P/N": None,
                    "S/N": None,
                    "P/N Description": None,
                    "Batch": None
                }

            current["P/N"] = clean[i + 1] if i + 1 < len(clean) else None

            if pn_assy is None:
                pn_assy = current["P/N"]

            i += 1

        elif value == "P/N S/N:":
            current["S/N"] = clean[i + 1] if i + 1 < len(clean) else None
            current["P/N Description"] = clean[i + 2] if i + 2 < len(clean) else None

            if sn_assy is None:
                sn_assy = current["S/N"]

            i += 2

        elif value == "Batch:":
            current["Batch"] = clean[i + 1] if i + 1 < len(clean) else None
            i += 1

        i += 1

    if any(current.values()):
        rows.append(current)

    df = pd.DataFrame(rows)

    # ---------- ADD ASSY ----------
    df.insert(0, "P/N Assy", pn_assy)
    df.insert(1, "S/N Assy", sn_assy)

    # (sementara) Source File untuk tracking internal
    df.insert(0, "Source File", uploaded_file.name)

    return df


# ================= MAIN =================
if uploaded_files:
    try:
        all_results = []

        for file in uploaded_files:
            df_result = process_file(file)
            all_results.append(df_result)

        # ---------- GABUNG SEMUA FILE ----------
        final_df = pd.concat(all_results, ignore_index=True)

        # ---------- CLEAN FINAL OUTPUT ----------
        # Hapus kolom Source File
        if "Source File" in final_df.columns:
            final_df = final_df.drop(columns=["Source File"])

        # Hapus duplicate berdasarkan Batch
        final_df = (
            final_df
            .drop_duplicates(subset=["Batch"], keep="first")
            .reset_index(drop=True)
        )

        # ---------- DISPLAY ----------
        st.success(f"{len(uploaded_files)} file berhasil diproses ✅")
        st.subheader("Hasil Akhir (Batch Unik)")
        st.dataframe(final_df, use_container_width=True)

        # ---------- DOWNLOAD ----------
        output = final_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download hasil (CSV) 🙏",
            output,
            file_name="Data NLA Hasil Olahan Program Veda Sepele🙏.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error("Terjadi error saat memproses file ❌")
        st.exception(e)
else:
    st.info("Silakan upload satu atau lebih file 🙏")
