package org.example;

import de.tu_dresden.inf.lat.evee.proofs.interfaces.IInference;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * @author Christian Alrabbaa
 *
 *         A convenient class to map elements of proofs to IDs
 */
public class GraphMLMapper<STATEMENT> {

	private final Map<IInference<STATEMENT>, Integer> inferenceToStr;
	private final Map<STATEMENT, Integer> axiomToStr;

	private final Map<Integer, IInference<STATEMENT>> strTOInference;
	private final Map<Integer, STATEMENT> strTOAxiom;

	private int id;

	public GraphMLMapper() {
		id = 0;
		strTOAxiom = new HashMap<>();
		strTOInference = new HashMap<>();
		axiomToStr = new HashMap<>();
		inferenceToStr = new HashMap<>();
	}


	public boolean addInferenceEntry(IInference<STATEMENT> inf) {
		Optional<IInference<STATEMENT>> infOpt;
		if (inf.getPremises().size() != 0)
			infOpt =  inferenceToStr.keySet().stream().filter(x->x.getRuleName().equals(inf.getRuleName())
					&& x.getPremises().equals(inf.getPremises())).findFirst();
		else
			infOpt = inferenceToStr.keySet().stream().filter(x->x.getRuleName().equals(inf.getRuleName())
					&& x.getConclusion().equals(inf.getConclusion())).findFirst();

		if(infOpt.isPresent())
			return false;

		inferenceToStr.put(inf, id);
		strTOInference.put(id, inf);
		id++;
		return true;
	}

	public boolean addStatementEntry(STATEMENT axiom) {
		if (!axiomToStr.containsKey(axiom)) {
			axiomToStr.put(axiom, id);
			strTOAxiom.put(id, axiom);
			id++;
			return true;
		}
		return false;
	}

	public int getInferenceID(IInference<STATEMENT> inf) {
		if(inferenceToStr.containsKey(inf))
			return inferenceToStr.get(inf);
		IInference<STATEMENT> key =  inferenceToStr.keySet().stream().filter(x->x.getRuleName().equals(inf.getRuleName())
				&& x.getPremises().equals(inf.getPremises())).findFirst().orElseThrow(null);
		return inferenceToStr.get(key);
	}

	public int getAxiomID(STATEMENT axiom) {
		return axiomToStr.getOrDefault(axiom, -1);
	}

	public IInference<STATEMENT> getIDInference(int idStr) {
		return strTOInference.get(idStr);
	}

	public STATEMENT getIDAxiom(int idStr) {
		return strTOAxiom.get(idStr);
	}

	public int getNextID() {
		return id++;
	}
}
