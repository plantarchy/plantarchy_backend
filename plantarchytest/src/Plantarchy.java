import java.awt.*;

public class Plantarchy {
    public static void main(String[] args) throws InterruptedException {
        Garden garden = new Garden(20, 20, 50);
        GUI gui = new GUI(garden);

        EventQueue.invokeLater(() -> {
            gui.setVisible(true);
        });

        garden.plantSeed(0, 0);
        garden.plantSeed(10, 10);

        while (true) {
            Thread.sleep(1000);
            gui.repaint();
        }
    }


}

