import "./CreateTask.css";
import Nav from "../../components/Nav/Nav";
import { useCreateTask } from "./use-create-task";


interface CreateTaskProperties {
    handleCreateTask: () => void;
}

export const CreateTask = ({ handleCreateTask }: CreateTaskProperties) => {

    const { isSigned,
        generatedKey,
        amount,
        targetPubKey,
        userPubKey,
        signature,
        response,
        handleSignTask,
        handleSubmit,
        handleGenerateKeys,
        setAmount,
        setTargetPubKey
    } = useCreateTask();

    return (
        <div className="create-task-container">
            <Nav handleCreateTask={handleCreateTask} />
            <h1>Crear nueva tarea</h1>
            {response &&
                <div className="response-container">
                    <p>
                        Transacción publicada
                    </p>
                    <input type="text" placeholder="Puede ser sarasa" value={response} readOnly />
                </div>
            }
            <label htmlFor="target_pub_key">pub_key destino</label>
            <input
                type="text"
                value={targetPubKey}
                onChange={(e) => setTargetPubKey(e.target.value)}
            />

            <label htmlFor="pub_key">Su pub_key HEX</label>
            <input type="text" placeholder="Puede ser sarasa" value={userPubKey} readOnly />

            <label htmlFor="cantidad">Cantidad</label>
            <input
                type="text"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
            />

            <label htmlFor="sign">Firma tarea</label>
            <input type="text" value={signature} readOnly />

            <div className="footer-buttons">
                <button className="button" disabled={generatedKey} onClick={handleGenerateKeys}>
                    Generar par de claves
                </button>
                <button className="button" disabled={!generatedKey || isSigned} onClick={handleSignTask}>
                    Firmar Tarea
                </button>
            </div>

            <button className="button enviar" onClick={handleSubmit} disabled={!isSigned}>
                Enviar Tarea
            </button>
        </div>
    );
};

export default CreateTask;
