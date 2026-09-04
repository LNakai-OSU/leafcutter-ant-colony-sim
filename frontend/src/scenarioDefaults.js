export function defaultsFromSchema(schema) {
  if (!schema) return {};
  return Object.fromEntries(schema.fields.map((f) => [f.key, f.default]));
}
