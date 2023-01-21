import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;

public class GUI extends JFrame {

    Garden garden;

    public GUI(Garden garden) {
        this.garden = garden;
        initUI();
    }

    private void initUI() {
        setTitle("Plantarchy");
        setSize(1000, 1000);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        this.repaint();
    }

    @Override
    public void paint(Graphics g) {
        super.paint(g);
        for (int i = 0; i < garden.grid.length; i++) {
            for (int j = 0; j < garden.grid[0].length; j++) {

                if (garden.getPlant(i,j) == null) {
                    g.setColor(Color.black);
                } else {
                    g.setColor(new Color(i*(255/garden.grid.length),j*(255/garden.grid[0].length),100));
                }

                g.fillRect(i*garden.cellSize,j*garden.cellSize,garden.cellSize,garden.cellSize);
            }
        }

        MouseListener l = new MouseAdapter()
        {
            public void mouseClicked(MouseEvent e)
            {
                int mouseX = e.getX();
                int mouseY = e.getY();


            }
        };
    }


}