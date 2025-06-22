import type { LastBlockChainedType } from "../../types/types";
import "./LastBlockChained.css";

interface LastBlockChainedProperties {
    lastChainedBlock: LastBlockChainedType
}
export const LastBlockChained = ({ lastChainedBlock }: LastBlockChainedProperties) => (
    lastChainedBlock.block_id != 0 ? (
        <div className="last-block-container">
            <div key={lastChainedBlock.block_id} className="data-container" >
                <h2>Último bloque encadenado</h2>
                <p><strong>Block ID:</strong> {lastChainedBlock.block_id}</p>
                <p><strong>Hash previo:</strong> {lastChainedBlock.previous_hash}</p>
                <p><strong>Nonce:</strong> {lastChainedBlock.nonce}</p>
                <p><strong>Minero:</strong> {lastChainedBlock.miner}</p>
                <p><strong>Prefijo:</strong> {lastChainedBlock.prefix}</p>
                <p><strong>Hash del bloque:</strong> {lastChainedBlock.block_hash}</p>
                <div>
                    <p className="subtitle">Transacción:</p>
                    <p><strong>Origen:</strong> {lastChainedBlock.transaction.source}</p>
                    <p><strong>Destino:</strong> {lastChainedBlock.transaction.target}</p>
                    <p><strong>Monto:</strong> {lastChainedBlock.transaction.amount}</p>
                    <p><strong>Timemstamp:</strong> {lastChainedBlock.transaction.timestamp}</p>
                    <p><strong>Descripcion:</strong> {lastChainedBlock.transaction.description}</p>
                    <p><strong>Firma:</strong> {lastChainedBlock.transaction.sign}</p>
                </div>
            </div >
        </div >
    ) : (
        <div>
            <p>Aun no hay bloques encadenados</p>
        </div>
    )
);


export default LastBlockChained;