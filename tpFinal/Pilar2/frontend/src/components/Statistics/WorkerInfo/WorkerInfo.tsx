import type { Worker } from "../../../types/types";
import "./WorkerInfo.css";

interface WorkerInfoProperties {
    workers: Worker[];
    showWorkers: boolean;
    setShowWorkers: (showWorkers: boolean) => void;
}

export const WorkerInfo = ({ workers, showWorkers, setShowWorkers }: WorkerInfoProperties) => (
    <div className='worker-info-container'>
        <p>Cantidad de workers registrados: <strong>{workers.length}</strong></p>
        <button className="button ver-mas" onClick={() => setShowWorkers(!showWorkers)}>
            {showWorkers ? "Ocultar detalles" : "Ver más"}
        </button>
        {
            showWorkers && (
                <div className="workers-details">
                    {workers.map((worker, index) => (
                        <div key={index} className="worker-card">
                            <p><strong>IP:</strong> {worker.ip}</p>
                            <p><strong>Tipo:</strong> {worker.info.type}</p>
                            <p><strong>Puerto:</strong> {worker.info.port}</p>
                            <p><strong>PubKey:</strong> {worker.info.pub_key}</p>
                        </div>
                    ))}
                </div>

            )
        }



    </div>
)