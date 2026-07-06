from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from env import get_db_conn
app = FastAPI()
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-G2ETPA9;"
    "DATABASE=RestaurantIntelligenceDB;"
    "Trusted_Connection=yes;"
)
templates = Jinja2Templates(directory="templates")
@app.get("/analytics/diagnostic")
def get_issue_diagnostic(issue_type: str):
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        # Query to find the top root causes for a SPECIFIC type of issue
        query = """
            SELECT root_cause, COUNT(*) as occurrence
            FROM Issues
            WHERE issue_type = ?
            GROUP BY root_cause
            ORDER BY occurrence DESC
        """
        cursor.execute(query, (issue_type,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {
                "issue_type": issue_type,
                "top_cause": "No data available",
                "breakdown": [],
                "ai_suggestion": "System stable. No recorded patterns for this issue type yet."
            }
            
        breakdown = [{"cause": r[0], "count": r[1]} for r in rows]
        primary_cause = rows[0][0]
        
        # Smart rule-based recommendations depending on what the root cause is
        suggestion = f"Investigate internal kitchen workflows regarding '{primary_cause}'."
        if "staff" in primary_cause.lower() or "chef" in primary_cause.lower():
            suggestion = "Action Required: Consider scheduling additional staff or conducting a training session."
        elif "ingredient" in primary_cause.lower() or "supply" in primary_cause.lower():
            suggestion = "Action Required: Review stock levels with your inventory management suppliers."
            
        return {
            "issue_type": issue_type,
            "top_cause": primary_cause,
            "breakdown": breakdown,
            "ai_suggestion": suggestion
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    # Notice we are passing the request as a named argument 'request=request'
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )

@app.get("/orders")
def get_orders():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        query = """SELECT o.order_id, c.customer_id, o.placed_time, o.completed_time, o.order_status
        FROM Orders o 
        INNER JOIN Customers c ON o.customer_id = c.customer_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        order_list = []
        for row in rows:
            order_list.append({
                "order_id": row.order_id,
                "customer_id": row.customer_id,
                "place_time": row.placed_time,
                "completed_time": row.completed_time,
                "status": row.order_status
            })
        return {"total_orders": len(order_list), "data": order_list}
    except Exception as e:
        return {"error": str(e)}

from typing import Optional

@app.get("/orders/issues")
def get_order_issues(issue_type: Optional[str] = None):
    try:
        con = get_db_conn()
        cursor = con.cursor()
        
        query = """
            SELECT i.issue_id, o.order_id, i.issue_type, i.detected_at, i.root_cause
            FROM Issues i 
            INNER JOIN Orders o ON i.order_id = o.order_id 
            WHERE 1=1
        """
        params = []
        if issue_type:
            query += " AND i.issue_type = ?"
            params.append(issue_type)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        con.close()
        issue_list = []
        for row in rows:
            issue_list.append({
                "issue_id": row.issue_id,
                "order_id": row.order_id,
                "issue_type": row.issue_type,
                "detected_at": row.detected_at,
                "root_cause": row.root_cause,
                "severity": "High" if row.issue_type in ["Delayed", "Incorrect Item"] else "Medium"
            })
        return {"total_issues": len(issue_list), "issues list": issue_list}
    except Exception as e:
        return {"error": str(e)}

@app.get("/menu")
def get_menu_items():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT item_id,item_name, category, expected_time FROM Menu_items")
        rows = cursor.fetchall()
        conn.close()
        menu_items = []
        for row in rows:
            menu_items.append({
                "item_id": row.item_id,
                "item_name": row.item_name,
                "category": row.category,
                "prep_time": row.expected_time
            })
        return {"menu": menu_items}
    except Exception as e:
        return {"error": str(e)}

@app.get("/feedback")
def get_feedback():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        query = """SELECT f.feedback_id, o.order_id, f.stars, f.comments 
        FROM Feedback f
        INNER JOIN Orders o ON f.order_id = o.order_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        feedback_list = []
        for row in rows:
            feedback_list.append({
                "feedback_id": row.feedback_id,
                "order_id": row.order_id,
                "rating": row.stars,
                "comments": row.comments
            })
        return {"total_feedback": len(feedback_list), "feedback": feedback_list}
    except Exception as e:
        return {"error": str(e)}

@app.get("/order_details")
def get_order_details():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        query = """
        SELECT o.order_id, i.item_id, oi.quantity, oi.notes FROM Order_items oi
        INNER JOIN Orders o ON o.order_id = oi.order_id
        INNER JOIN Menu_items i ON oi.item_id = i.item_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        order_details_list = []
        for row in rows:
            order_details_list.append({
                "order_id": row.order_id,
                "item_id": row.item_id,
                "quantity": row.quantity,
                "notes": row.notes
            })
        return {"total_orders": len(order_details_list), "order_details": order_details_list}
    except Exception as e:
        return {"error": str(e)}

@app.get("/customer")
def get_customers():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id, name, phone_no, account_created_date FROM Customers")
        rows = cursor.fetchall()
        conn.close()
        customer_list = []
        for row in rows:
            customer_list.append({
                "customer_id": row.customer_id,
                "name": row.name,
                "contact_info": row.phone_no,
                "account_created_date": row.account_created_date
            })
        return {"total_customers": len(customer_list), "customers": customer_list}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/analytics/summary")
def get_analysis_summary():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        # 1. Count total issues
        cursor.execute("SELECT COUNT(*) FROM Issues")
        total_issues = cursor.fetchone()[0]
        
        # 2. Find the most common root cause
        cursor.execute("SELECT TOP 1 root_cause, COUNT(*) as count FROM Issues GROUP BY root_cause ORDER BY count DESC")
        top_cause = cursor.fetchone()
        
        conn.close()

        return {
            "summary": {
                "total_recorded_issues": total_issues,
                "primary_failure_reason": top_cause[0] if top_cause else "None",
                "recommendation": "Investigate " + top_cause[0] if top_cause else "System stable"
            }
        }
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/analysis/customer-impact")
def get_customer_impact():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        # This joins Issues, Orders, and Feedback all together
        query = """
            SELECT i.issue_type, f.stars, f.comments 
            FROM Issues i
            JOIN Orders o ON i.order_id = o.order_id
            JOIN Feedback f ON o.order_id = f.order_id
            WHERE f.stars <= 2
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        impact_list = [{"issue": r[0], "rating": r[1], "comment": r[2]} for r in rows]
        return {"unhappy_customers_due_to_issues": impact_list}
    except Exception as e:
        return {"error": str(e)}
@app.get("/analytics/health-check")
def get_restaurant_health():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        # 1. Get total number of orders
        cursor.execute("SELECT COUNT(*) FROM Orders")
        total_orders = cursor.fetchone()[0]
        
        # 2. Get total number of issues
        cursor.execute("SELECT COUNT(*) FROM Issues")
        total_issues = cursor.fetchone()[0]
        
        conn.close()

        # 3. Calculate the percentage (The "Analyzer" part)
        if total_orders == 0:
            return {"message": "No data available yet."}
            
        success_rate = ((total_orders - total_issues) / total_orders) * 100
        
        return {
            "total_orders": total_orders,
            "total_issues": total_issues,
            "health_score": f"{success_rate:.2f}%",
            "status": "Healthy" if success_rate > 90 else "Action Required"
        }
    except Exception as e:
        return {"error": str(e)}
@app.get("/analytics/top-issue-item")
def get_top_issue_item():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        query = """
            SELECT TOP 1 m.item_name, COUNT(i.issue_id) as issue_count
            FROM Issues i
            JOIN Order_details oi ON i.order_id = oi.order_id
            JOIN Menu_items m ON oi.item_id = m.item_id
            GROUP BY m.item_name
            ORDER BY issue_count DESC
        """
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "problematic_item": result[0],
                "number_of_issues": result[1],
                "recommendation": f"Review the preparation process for {result[0]}."
            }
        return {"message": "No issues found for any items."}
    except Exception as e:
        return {"error": str(e)}
from pydantic import BaseModel
from datetime import datetime

# This defines what information we need when adding a new issue
class IssueImport(BaseModel):
    order_id: int
    issue_type: str
    root_cause: str

@app.post("/issues/import")
def import_issue(issue: IssueImport):
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        # SQL query to insert a new issue into your Issues table
        query = """
            INSERT INTO Issues (order_id, issue_type, detected_at, root_cause)
            VALUES (?, ?, ?, ?)
        """
        # datetime.now() automatically records the exact time the issue was reported
        cursor.execute(query, (issue.order_id, issue.issue_type, datetime.now(), issue.root_cause))
        
        conn.commit()  # This saves the changes to SQL Server
        conn.close()
        return {"status": "success", "message": "Issue logged successfully!"}
    except Exception as e:
        return {"error": str(e)}
@app.get("/analytics/monthly-report")
def get_monthly_report():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        # This query groups your issues by the month they happened
        query = """
            SELECT DATENAME(month, detected_at) as MonthName, COUNT(*) as IssueCount
            FROM Issues
            GROUP BY DATENAME(month, detected_at), MONTH(detected_at)
            ORDER BY MONTH(detected_at)
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        report = [{"month": row[0], "issues_count": row[1]} for row in rows]
        return {"monthly_analysis": report}
    except Exception as e:
        return {"error": str(e)}