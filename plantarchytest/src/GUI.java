import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

public class GUI extends JFrame {

    Garden garden;
    public final int GARDEN_X = 100;
    public final int GARDEN_Y = 100;

    public GUI(Garden garden) {
        this.garden = garden;
        initUI();
        addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                int mouseX = e.getX();
                int mouseY = e.getY();
                System.out.println("cell clicked");
                garden.cellClicked(mouseX - GARDEN_X, mouseY - GARDEN_Y);
                repaint();
            }
        });

    }

    private void initUI() {
        setTitle("Plantarchy");
        setSize(1000 + GARDEN_X, 1000 + GARDEN_Y);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        this.repaint();
    }

    @Override
    public void paint(Graphics g) {
        super.paint(g);
        for (int i = 0; i < garden.grid.length; i++) {
            for (int j = 0; j < garden.grid[0].length; j++) {

                if (garden.getPlant(i, j) == null) {
                    g.setColor(Color.LIGHT_GRAY);
                } else {
                    g.setColor(new Color(i * (255 / garden.grid.length), j * (255 / garden.grid[0].length), 100));
                }

                g.fillRect(+GARDEN_X + i * garden.cellSize, +GARDEN_Y + j * garden.cellSize, garden.cellSize, garden.cellSize);
            }
        }
    }


}