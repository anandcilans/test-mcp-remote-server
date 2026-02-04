from fastmcp import FastMCP
import json

# Initialize the MCP server with a descriptive name
mcp = FastMCP("BMICalculator")


@mcp.tool()
def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """
    Calculate Body Mass Index (BMI) given weight (kg) and height (cm).
    Returns a dictionary with BMI value and category.
    """
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
    return {
        "status": "success",
        "bmi": round(bmi, 2),
        "category": category,
    }


@mcp.resource("info://server")
def server_info() -> str:
    """
    Get information about this server.
    """
    info = {
        "name": "BMI Calculator MCP Server",
        "version": "1.0.0",
        "description": "A simple MCP server for BMI calculation.",
        "tools": ["calculate_bmi"],
        "author": "Your Name",
    }
    return json.dumps(info, indent=2)


if __name__ == "__main__":
    # For MCPCloud, you usually do not need to specify host/port
    mcp.run()
