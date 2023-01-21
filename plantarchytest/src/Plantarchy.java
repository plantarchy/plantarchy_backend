import java.awt.*;

public class Plantarchy {
    public static void main(String[] args) throws InterruptedException{
        Garden garden = new Garden(20,20,50);
        GUI gui = new GUI(garden);

        EventQueue.invokeLater(() -> {
            gui.setVisible(true);
        });


        while(true) {
            Thread checkForClick = new Update();
            Thread.sleep(100);
            checkForClick.join();
            gui.repaint();
        }
    }
}

class Update extends Thread {

    @Override
    public void run() {
        super.run();

    }
}
