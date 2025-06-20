import Blockchain from "../pages/Blockchain/Blockchain";
import GenesisBlock from "../pages/GenesisBlock/GenesisBlock";
import "./BlockchainViewer.css";
import { useBlockchainViewer } from "./use-blockchain-viewer"
import CreateTask from "../pages/CreateTask/CreateTask";


const BlockchainViewer = () => {

    const { fetchBlockchain,
        fetchGenesisBlock,
        handleCreateTask,
        blockchain,
        genesisBlock,
        createTask,
        error,
    } = useBlockchainViewer();

    return (
        <div className="">
            {createTask ?
                <CreateTask handleCreateTask={handleCreateTask} /> :
                <>
                    <div className='botonera'>
                        <button
                            onClick={fetchBlockchain}
                            className="blockchain-button"
                        >
                            Obtener Blockchain
                        </button>

                        <button
                            onClick={fetchGenesisBlock}
                            className="blockchain-button"
                        >
                            Obtener Bloque GENESIS
                        </button>
                    </div>
                    <div className="botonera-footer">
                        <button
                            onClick={handleCreateTask}
                            className="task-button"
                        >
                            Crear Tarea
                        </button>
                    </div>


                    {error && <p className="text-red-500 mt-4">{error}</p>}

                    {blockchain && <Blockchain blocks={blockchain} />}
                    {genesisBlock && <GenesisBlock genesisBlock={genesisBlock} />}
                </>
            }

        </div>
    );
};

export default BlockchainViewer;
