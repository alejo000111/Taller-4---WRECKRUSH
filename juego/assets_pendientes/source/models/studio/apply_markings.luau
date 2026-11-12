local MaterialService = game:GetService("MaterialService")

local PAINTED = { "Crosswalk", "EdgeLine", "CenterLine", "LaneDash", "SafetyLine", "HazardStripe" }
local SIDEWALK = { "Sidewalk" }

local function variantFolder()
	local folder = MaterialService:FindFirstChild("Wreckrush")
	if not folder then
		folder = Instance.new("Folder")
		folder.Name = "Wreckrush"
		folder.Parent = MaterialService
	end
	return folder
end

local function makeVariant(name, base, ids, studs)
	local folder = variantFolder()
	local variant = folder:FindFirstChild(name) or Instance.new("MaterialVariant")
	variant.Name = name
	variant.BaseMaterial = base
	variant.ColorMap = ids.color
	variant.NormalMap = ids.normal
	variant.RoughnessMap = ids.roughness
	if ids.metalness then
		variant.MetalnessMap = ids.metalness
	end
	variant.StudsPerTile = studs
	variant.Parent = folder
	return variant
end

local function apply(names, material, variantName)
	local wanted = {}
	for _, n in names do
		wanted[n] = true
	end
	local count = 0
	for _, d in workspace.Map:GetDescendants() do
		if d:IsA("BasePart") and wanted[d.Name] and d:GetAttribute("WRMesh") == nil then
			d.Material = material
			d.MaterialVariant = variantName
			count += 1
		end
	end
	return count
end

return function(roadPaintIds)
	makeVariant("WR_RoadPaint", Enum.Material.SmoothPlastic, roadPaintIds, 6)
	local painted = apply(PAINTED, Enum.Material.SmoothPlastic, "WR_RoadPaint")
	local walks = apply(SIDEWALK, Enum.Material.Pavement, "WR_Sidewalk")
	return string.format("road paint x%d, sidewalk x%d", painted, walks)
end
