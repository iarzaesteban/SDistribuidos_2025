import type { GenesisBlockType } from "../../types/types";
import "./GenesisBlock.css";

interface BlockchainProperties {
    genesisBlock: GenesisBlockType
}

export const GenesisBlock = ({ genesisBlock }: BlockchainProperties) => (
    
    <div className="blockchacin-container">
        <div key={genesisBlock.block_id} className="data-container">
            <h2>Bloque GENESIS</h2>
            <p><strong>Block ID:</strong> {genesisBlock.block_id}</p>
            <p><strong>Hash:</strong> {genesisBlock.block_hash}</p>
            <p><strong>Nombre del Bloque:</strong> {genesisBlock.transaction.block_name}</p>
            <div>
                <p className="subtitle">Configuracion:</p>
                <p><strong>Cantidad de intentos:</strong> {genesisBlock.config.max_tries_per_tx}</p>
                <p><strong>Inicio ventana solicitar tareas:</strong> {genesisBlock.config.monitoring_window_start}</p>
                <p><strong>Fin ventana para solicitar tareas:</strong> {genesisBlock.config.monitoring_window_end}</p>
                <p><strong>Inicio ventana para publicar transacciones:</strong> {genesisBlock.config.publish_window_start}</p>
                <p><strong>Fin ventana para publicar transacciones:</strong> {genesisBlock.config.publish_window_end}</p>
                <p><strong>Tiempo para un ciclo:</strong> {genesisBlock.config.window_period_seconds}</p>
            </div>
        </div>

    </div>
);

export default GenesisBlock;
