import Blockchain from "../pages/Blockchain/Blockchain";
import GenesisBlock from "../pages/GenesisBlock/GenesisBlock";
import "./BlockchainViewer.css";
import { useBlockchainViewer } from "./use-blockchain-viewer"
import CreateTask from "../pages/CreateTask/CreateTask";
import { LastBlockChained } from "./LastBlockChained/LastBlockChained";
import { useState } from "react";
import StressTasks from "../pages/StressTasks/StressTasks";


const BlockchainViewer = () => {

    const { fetchBlockchain,
        fetchGenesisBlock,
        handleCreateTask,
        handleStressTask,
        fetchLastChainedBlock,
        blockchain,
        genesisBlock,
        lastChainedBlock,
        error,
    } = useBlockchainViewer();

    const [activeTab, setActiveTab] = useState<string>("blockchain");

    const handleTabChange = (tab: string) => {
        setActiveTab(tab);

        switch (tab) {
            case "blockchain":
                fetchBlockchain();
                break;
            case "genesis":
                fetchGenesisBlock();
                break;
            case "last":
                fetchLastChainedBlock();
                break;
            case "create":
                handleCreateTask();
                break;
            case "stress":
                handleStressTask();
                break;
            default:
                break;
        }
    };

    return (
        <div className="blockchain-viewer-container">
            <aside className="sidebar">
                <ul>
                    <li onClick={() => handleTabChange("blockchain")}>Blockchain</li>
                    <li onClick={() => handleTabChange("genesis")}>Bloque GENESIS</li>
                    <li onClick={() => handleTabChange("last")}>Último Bloque Encadenado</li>
                    <li onClick={() => handleTabChange("create")}>Crear Tarea</li>
                    <li onClick={() => handleTabChange("stress")}>Stress Tareas</li>

                </ul>
            </aside>

            <main className="main-content">
                {error && <p className="text-red-500 mt-4">{error}</p>}

                {activeTab === "blockchain" && blockchain && <Blockchain blocks={blockchain} />}
                {activeTab === "genesis" && genesisBlock && <GenesisBlock genesisBlock={genesisBlock} />}
                {activeTab === "last" && lastChainedBlock && <LastBlockChained lastChainedBlock={lastChainedBlock} />}
                {activeTab === "create" && <CreateTask />}
                {activeTab === "stress" && <StressTasks />}
                
            </main>
        </div>
    );
};

export default BlockchainViewer;
