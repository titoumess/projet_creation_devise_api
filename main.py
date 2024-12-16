from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_connection

app = FastAPI()

class TauxChange(BaseModel):
    id_devise: int
    date: str
    taux_change: float

@app.get("/rates/{id_devise}")
def get_currency_rate(id_devise: int):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM taux_change WHERE id_devise = %s", (id_devise,))
    rates = cursor.fetchall()
    conn.close()
    if not rates:
        raise HTTPException(status_code=404, detail="Currency not found")
    return rates

@app.post("/rates/")
def add_currency_rate(rate: TauxChange):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO taux_change (id_devise, date, taux_change) VALUES (%s, %s, %s)",
                   (rate.id_devise, rate.date, rate.taux_change))
    conn.commit()
    conn.close()
    return {"message": "Rate added successfully"}