from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer", host="127.0.0.1", port=8050)

# Add your tools and resources here...
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)


if __name__ == "__main__":
    # Run with SSE transport on port 8000
    mcp.run(transport="sse")