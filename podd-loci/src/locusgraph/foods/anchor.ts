// Anchor (root) food context for a user.
// Extends the user's person context and links down to meal-type children.
//
// context_id example: "nasim_u123:foods"
// extends:           ["person:nasim_u123"]
//
// Graph:  person:nasim_u123  <──  nasim_u123:foods  ──>  foods:breakfast
//                                                    ──>  foods:lunch
//                                                    ──>  foods:dinner
//                                                    ──>  foods:snack

import { userPersonContext } from "../user.js";

interface MasterFoodEventInput {
  name: string;
  user_id: string;
}

export function anchorFoodContext(name: string, user_id: string) {
  return `${name}_${user_id}:foods`;
}

export function anchorFoodEventPayload({
  name,
  user_id,
}: MasterFoodEventInput) {
  return {
    context_id: anchorFoodContext(name, user_id),
    event_kind: "fact" as const,
    source: "system" as const,
    payload: `this memories link to these context foods:breakfast, foods:lunch, foods:dinner, foods:snack`,
    extends: [userPersonContext(name, user_id)],
  };
}
