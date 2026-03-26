# MIP_1.praktiskais_darbs

# Dalīšanas spēle (Cilvēks vs Dators)

## Projekta apraksts
Šī programma realizē spēli starp cilvēku un datoru, kur spēles pamatā ir skaitļa dalīšana ar noteiktiem dalītājiem. Spēlē tiek izmantoti mākslīgā intelekta algoritmi – **Minimax** un **Alpha-Beta**.

Spēles mērķis ir, veicot gājienus, iegūt izdevīgāku gala rezultātu nekā pretiniekam.

---

## Spēles noteikumi

1. Spēle sākas ar nejauši izvēlētu skaitli diapazonā no **40000 līdz 50000**, kas dalās ar **60**.
2. Spēlētāji pārmaiņus veic gājienus.
3. Katrā gājienā drīkst dalīt skaitli tikai ar:
   - `3`
   - `4`
   - `5`
4. Dalīšana ir atļauta tikai tad, ja skaitlis dalās bez atlikuma.
5. Pēc katra gājiena:
   - ja jaunais skaitlis ir **pāra**, punktiem pieskaita **+1**
   - ja **nepāra**, punktiem pieskaita **-1**
6. Ja jaunais skaitlis **beidzas ar 0 vai 5**, bankai pieskaita **+1**
7. Spēle beidzas, kad vairs nav iespējams veikt nevienu gājienu.

---

## Gala rezultāts

Kad spēle beidzas:

- Ja punktu skaits ir **pāra skaitlis**:  
  `rezultāts = punkti - banka`

- Ja punktu skaits ir **nepāra skaitlis**:  
  `rezultāts = punkti + banka`

Uzvarētājs:
- Ja gala rezultāts ir **pāra skaitlis** → uzvar **cilvēks**
- Ja gala rezultāts ir **nepāra skaitlis** → uzvar **dators**

---

## Kā palaist programmu

Nepieciešams Python 3.

Terminālī izpildi:

```bash
python main.py
