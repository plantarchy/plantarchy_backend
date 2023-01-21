public class Garden {

    public Plant[][] grid;
    public int cellSize;

    public Garden(int width, int height, int cellSize) {
        grid = new Plant[width][height];
        this.cellSize = cellSize;
    }

    public Plant getPlant(int x, int y) {
        return grid[x][y];
    }

    public void plantSeed(int x, int y) {
        grid[x][y] = new Plant();
    }

    public void cellClicked(int x, int y) {
        int cellX = x / cellSize;
        int cellY = y / cellSize;

        plantSeed(cellX, cellY);
    }
}
