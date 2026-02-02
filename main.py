# BMI Calculator MCP Server
from fastmcp import FastMCP
import json

mcp = FastMCP("BMICalculator")

@mcp.tool()
def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """
    Calculate Body Mass Index (BMI) given weight (kg) and height (cm).
    Returns BMI value and category.
    """
    try:
        if height_cm <= 0 or weight_kg <= 0:
            return {
                "status": "error",
                "message": "Height and weight must be positive numbers.",
            }
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m**2)
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obesity"
        return {"status": "success", "bmi": round(bmi, 2), "category": category}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Resource: Server information
@mcp.resource("info://server")
def server_info() -> str:
    """Get information about this server."""
    info = {
        "name": "Simple Calculator Server",
        "version": "1.0.0",
        "description": "A basic MCP server with math tools",
        "tools": ["add", "random_number"],
        "author": "Your Name",
    }
    return json.dumps(info, indent=2)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
